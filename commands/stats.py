# ? Imports
from json import dumps

from telebot import types, apihelper
from config import bot, commands
from data_base import Chats, ResponsesManager
from help_funcs import getDeleteMarkup, stringForStats, addUrlButton


# * Command
@bot.message_handler(commands=[commands['s']])
def sendStats(message):
  """
  Sends a message with all words information in a special formated string,
  which is provide by 'stringsForStats' functionm. Gets informations from the
  database and splits the result of the funcion unsing built-in 'untils' methods.
  """

  chatID = message.chat.id
  clearButton = types.InlineKeyboardButton(
    message.replies.skeyboard[0],
    callback_data=dumps(['toClearTrue', chatID])
  )

  # * Getting info from the DB to pass into the function
  currentChat = Chats.getChat(chatID)
  wordObjects = currentChat.words
  wordNumbers = [word.sentTimes for word in wordObjects]
  words = [word.text for word in wordObjects]

  sendToPrivate = Chats.getSettings(chatID)['sendPrivate']

  chatName = None
  if sendToPrivate:
    chatName = message.chat.username

  formatedStrings = stringForStats(chatID, words, wordNumbers, True, chatName)
  markup = None

  # * Allowes to save message ids. More info in the class doc string
  editor = ResponsesManager(currentChat)

  if not formatedStrings:
    tempMessage = bot.send_message(message.chat.id, message.replies.nos)
    editor.addIDs(message.message_id, tempMessage)
    return

  # * If specified in settings will set chatID variable to users chat id,
  # * so the statistics will be sent not to the chat but to user pesonaly.
  if sendToPrivate:
    chatID = message.from_user.id

  if formatedStrings:
    # * Sending a splited message and adding an inline keyboard to the last element,
    # * so the user will be able to everything faster and more comftable.

    try:
      for index, part in enumerate(formatedStrings):
        if index + 1 == len(formatedStrings):
          markup = getDeleteMarkup(commands.s, message, clearButton)
          if message.chat.username and Chats.getSettings(message.chat.id)['sendPrivate']:
            addUrlButton(markup, message.replies.goToChat[0], message.chat.username)


        tempMessage = bot.send_message(
          chatID, part,
          reply_markup=markup, disable_notification=True, parse_mode='html'
        )

        editor.addIDs(message.message_id, tempMessage, chatID)

      if Chats.getSettings(message.chat.id)['sendPrivate'] and message.chat.type != 'private':
        markup = types.InlineKeyboardMarkup()
        addUrlButton(markup, message.replies.goToBot[1], bot.get_me().username)

        editor.addIDs(
          message.message_id,
          bot.send_message(
            message.chat.id,
            message.replies.s[2].format(
              bot.get_me().username
            ),
            reply_markup=markup
          ))

    except apihelper.ApiException as e:
      print(e)
      editor.addIDs(
        message.message_id,
        bot.send_message(
          message.chat.id,
          message.replies.s[3].format(
            bot.get_me().username
      )))
