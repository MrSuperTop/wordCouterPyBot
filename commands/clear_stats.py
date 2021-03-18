# ? Imports
from config import bot, commands
from data_base import Chats, Word


# * Command
@bot.message_handler(commands=[commands['cs']])
def clearStats(message):
  """
  Clears the Chat object for current chat, so there will be no information
  to use left, but it leaves the object in the database,
  so there will be no need to create a new one
  """

  # * Cleaning the chat Document
  currentChat = Chats.getChat(message.chat.id)
  currentChat.words = []
  currentChat.sentMessages = currentChat.sentWords = 0
  currentChat.topWord = Word(text='', sentTimes=0)
  currentChat.save()

  # adder = IDAdder(currentChat,)
  bot.send_message(message.chat.id, message.replies.sclrd)
