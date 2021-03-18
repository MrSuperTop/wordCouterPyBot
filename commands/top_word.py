# ? Impotrs
from config import bot, commands
from data_base import Chats
from help_funcs import getDeleteMarkup


# * Command
@bot.message_handler(commands = [commands['tw']])
def sendTopWord(message):
  """Gets from the DB most commonly used word objects and sends it to the chat"""

  chatID = message.chat.id

  currentChat = Chats.getChat(chatID)
  topWord = currentChat.topWord

  if topWord.text:
    toSend = message.replies.tw.format(topWord.text, topWord.sentTimes)

    bot.send_message(chatID, toSend, reply_markup=getDeleteMarkup(commands.tw, message))
  else:
    bot.send_message(chatID, message.replies.nos)
