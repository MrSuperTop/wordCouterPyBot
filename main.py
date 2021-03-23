
# ? Imports
# * Built-in modules
from json import loads

# * Telegram Liblary
from telebot import types, apihelper

apihelper.ENABLE_MIDDLEWARE = True

from config import bot
from fun_stuff import *
from help_funcs import *

# * Modules needed to work with mongoDB and those using them to get info
from data_base import ResponsesManager, Word, Chats, checkChat, ResponsesManager, Settings
from language import Language

# ? Commands
# * Will run all commands in the commands folder throungh __init__.py
import commands as cmnds
cmnds.runCommands()

savedMessageID = -1

# ? Middleware
# * Message editing for simple handles and edding bot responses to the DB
@bot.middleware_handler(update_types=['message'])
def modifyMessage(bot_instance, message):
  chatID = message.chat.id
  checkChat(chatID)
  currentChat = Chats.getChat(chatID)

  # * Setting bot replies
  message.replies = Language(message.chat.id).strs

  # ? Settings
  # * Checking if a message id an a chat id match a those which are in the DB.
  # * Then we assume, that the message it's a new value for a setting, so we
  # * change it.

  editMessageInfo = currentChat.settings.editMessageInfo
  if (editMessageInfo and
      editMessageInfo['requestMessageId'] + 1 == message.message_id and
      editMessageInfo['requestChatId'] == message.chat.id):
    editArgument = message.text.split()[0]

    try:
      # * Changing setting value and sending user a reponse
      originalChatId = editMessageInfo['originalChatId']
      chatWeToChange = Chats.getChat(originalChatId)
      strings = Language(originalChatId).strs
      originalChat = Chats.getChat(originalChatId)

      Settings.setSettingValue(
        chatWeToChange,
        editMessageInfo['commandName'],
        int(editArgument)
      )

      bot.edit_message_text(
        strings.stg.msgTitle,
        originalChat.ID,
        originalChat.settings.lastMessageId[0],
        reply_markup=settingsMarkup(originalChatId)
      )

      # * Clearing used info
      currentChat.settings.editMessageInfo = {}

      # * Answering
      bot.answer_callback_query(
        editMessageInfo['callbackId'],
        message.replies.stg.changeSuccess
      )
    except ValueError:
      bot.send_message(chatID, message.replies.stg.valueIsWrong)

  # ? Resposes
  # * Saving bot responses to the DB trough ReponsesManager class and deleting old messages
  if not message.text is None and '/' in message.text:
    deleteAfter = currentChat.settings['removeAfter']['value']

    editor = ResponsesManager(currentChat)
    editor.addResponse(message.message_id)

    try:
      # * Deleting a reponse and all connected messages. Will delete everywhere
      if len(currentChat.responses) > deleteAfter:
        # * Spltting information about the oldest reponses into variables and deleting
        # * "main" nessage + other message, which were sent when the command was sent

        # * Splitting info to access it easier
        oldestResponse = list(currentChat.responses.items())[0]
        oldestResponseChatId = oldestResponse[0]
        oldestResponseIds = oldestResponse[1]['connectedIDs']

        # * Deleting data from the DB and removing "main" message in the chat
        editor.deleteResponse(oldestResponseChatId)
        bot_instance.delete_message(chatID, oldestResponseChatId)

        # * Deleting other messages
        if oldestResponseIds:
          for chatId, addtionalIds in oldestResponseIds.items():
            if not isinstance(addtionalIds, list):
              addtionalIds = [addtionalIds]

            for id in addtionalIds:
              bot_instance.delete_message(chatId, id)

    except apihelper.ApiException as error:
      print(error)

    currentChat.save()

# * Updating call parameter to save strings and some aditional
# * info needed for deleting messages properly

@bot.middleware_handler(update_types=['callback_query'])
def modifyCall(bot_instance, call):
  checkChat(call.message.chat.id)
  call.replies = Language(call.message.chat.id).strs

  # * Getting info from the call.data if an array in json was passed
  if '"' in call.data:
    call.additionalInfo = loads(call.data)[1]
    call.data = loads(call.data)[0]

# ? Handlers
# * Text message handler
@bot.message_handler(content_types=['text'])
def countWords(message):
  """
  Handles text messages. Upates and save new information to the database,
  so it will be up-to-date to the real chat history. It's a main part of this bot
  """

  global savedMessageID

  # * If a message contains a slash and it wasn't handled yet, command doesn' exist
  if message.text.strip()[0] == '/':
    bot.send_message(message.chat.id, message.replies.cnf)

  elif not 'http' in message.text:
    splitedMessage = splitSentence(message.text)

    if '' not in splitedMessage:
      # * Checking if current chat exists in the database an getting its object to use
      currentChat = Chats.getChat(message.chat.id)

      # * Update "counters" in database
      currentChat.sentWords += len(splitedMessage)
      currentChat.sentMessages += 1

      wordsList = []
      for part in splitedMessage:
        wordLower = part.lower()

        # * Adds a word in the list, if it's not fond in it
        wordsList = [word.text for word in currentChat.words]
        if not wordLower in wordsList or not currentChat.words:
          # * Adds new Word object object to the DB if there is't any
          tempWord = Word(
            text = wordLower,
            sentTimes = 1
          )

          currentChat.words.append(tempWord)

        # * Incriments the number of the word if it's found in the list
        else:
          # * Doing the same stuff, but in mongoDB
          for word in currentChat.words:
            if word.text == wordLower:
              word.sentTimes += 1
              break

        # * Updating the topWord object in the DB
        wordNumbers = [word.sentTimes for word in currentChat.words]
        topSentTimes = currentChat.topWord.sentTimes

        if topSentTimes < max(wordNumbers) or not currentChat.topWord.text:
          wordsList = [word.text for word in currentChat.words]
          topIndex = wordNumbers.index(max(wordNumbers))

          currentChat.topWord = Word(
            text = wordsList[topIndex],
            sentTimes = max(wordNumbers)
          )

      print('savingTheDB')
      currentChat.save()

@bot.callback_query_handler(func=lambda call: call.data)
def callbackInline(call):
  """Function to control inline buttonsm won't be used anywhere, just in the decorator"""

  if call.message:
    chatID = call.message.chat.id

    if call.data == 'toClearTrue':
      markup = types.InlineKeyboardMarkup(row_width = 1)
      keyboardItem1 = types.InlineKeyboardButton(call.replies.skeyboard[1], callback_data = 'deleteMessage')
      markup.add(keyboardItem1)

      bot.delete_message(chatID, call.message.message_id - 1)
      bot.edit_message_text(call.message.text, chatID, call.message.message_id, reply_markup = markup)

      # * Cleaning the chat Document
      currentChat = Chats.getChat(call.additionalInfo)
      currentChat.words = []
      currentChat.sentMessages = currentChat.sentWords = 0
      currentChat.topWord = Word(text='', sentTimes=0)
      currentChat.save()

      bot.send_message(chatID, call.replies.sclrd)

    if call.data == 'deleteMessage':
      bot.answer_callback_query(call.id, show_alert=False, text=call.replies.notf[0])
      bot.delete_message(chatID, call.message.message_id)
    if call.data == 'deleteWithCommand':
      bot.answer_callback_query(call.id, show_alert=False, text=call.replies.notf[1])
      bot.delete_message(chatID, call.message.message_id)
      bot.delete_message(chatID, call.additionalInfo) # ! HERE

    # * Handles changing language settings
    if call.data == 'setLangRu':
      Language(chatID).lang = (call, 'ru')

    if call.data == 'setLangEng':
      Language(chatID).lang = (call, 'eng')

    if call.data == 'setLangEng' or call.data == 'setLangRu':
      call.replies = Language(chatID).strs
      bot.answer_callback_query(call.id, show_alert = False, text = call.replies.sectl[1])
      bot.delete_message(chatID, call.message.message_id)

bot.polling(none_stop=True)
