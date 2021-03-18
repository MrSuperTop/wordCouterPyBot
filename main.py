
# ? Imports
# * Built-in modules
from json import loads
from dotenv import main

# * Telegram Liblary
from telebot import types, util, apihelper

apihelper.ENABLE_MIDDLEWARE = True

# * Config
import config
from config import commands, dotdict, bot

# * Local files
from fun_stuff import *
from help_funcs import *

# * Modules needed to work with mongoDB and those using them to get info
from data_base import ResponsesManager, Word, Chats, checkChat, ResponsesManager
from language import Language

# ? Commands
# * Will run all commands in the commands folder throungh __init__.py
import commands as cmnds
cmnds.runCommands()

savedMessageID = -1

# ? Middleware
@bot.middleware_handler(update_types=['message'])
def modifyMessage(bot_instance, message):
  chatID = message.chat.id
  checkChat(chatID)

  # ? Saving bot responses to the DB trough ReponsesManager class and deleting old messages
  if '/' in message.text:
    currentChat = Chats.getChat(chatID)
    deleteAfter = currentChat.settings['removeAfter']['numberOfMessages']

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

    # * Setting replies and saving the db
    message.replies = Language(message.chat.id).strs
    currentChat.save()

@bot.middleware_handler(update_types=['callback_query'])
def modifyCall(bot_instance, call):
  checkChat(call.message.chat.id)
  call.replies = Language(call.message.chat.id).strs

  if '"' in call.data:
    call.commandID = loads(call.data)[1]
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

  if '/' in message.text:
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

        if currentChat.topWord.sentTimes > max(wordNumbers):
          wordsList = [word.text for word in currentChat.words]
          topIndex = wordNumbers.index(max(wordNumbers))

          currentChat.topWord = Word(
            text = wordsList[topIndex],
            sentTimes = max(wordNumbers)
          )

        # * Saving all changes
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
      bot.edit_message_text(chat_id = chatID, message_id = call.message.message_id, text = call.message.text, reply_markup = markup)

      # * Cleaning the chat Document
      currentChat = Chats.getChat(chatID)
      currentChat.words = []
      currentChat.sentMessages = currentChat.sentWords = 0
      currentChat.topWord = Word(text='', sentTimes=0)
      currentChat.save()

      bot.send_message(chatID, call.replies.sclrd)

    if call.data == 'deleteMessage':
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=call.replies.notf[0])
      bot.delete_message(chatID, call.message.message_id)
    if call.data == 'deleteWithCommand':
      bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=call.replies.notf[1])
      bot.delete_message(chatID, call.message.message_id)
      bot.delete_message(chatID, call.commandID) # ! HERE

    # * Handles changing language settings
    if call.data == 'setLangRu':
      Language(chatID).lang = (call, 'ru')

    if call.data == 'setLangEng':
      Language(chatID).lang = (call, 'eng')

    if call.data == 'setLangEng' or call.data == 'setLangRu':
      call.replies = Language(chatID).strs
      bot.answer_callback_query(callback_query_id=call.id, show_alert = False, text = call.replies.sectl[1])
      bot.delete_message(chatID, call.message.message_id)
      # bot.answer_callback_query(call.id, "Answer is Yes", True)

bot.polling(none_stop=True)
