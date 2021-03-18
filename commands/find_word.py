# ? Imports
from config import bot, commands
from data_base import Chats
from help_funcs import extractArgs, stringForStats
from language import Language


# * Command
@bot.message_handler(commands=[commands['fw']])
def findWord(message):
  """Will look for the requested word in the database and send inforamation about it"""

  args = extractArgs(message.text)
  chatID = message.chat.id
  currentChat = Chats.getChat(chatID)

  # * Checking if the arguments where provided
  if not args:
    bot.send_message(chatID, message.replies.fw[2])
    return

  # * Looking for words saving info about them and sending the result
  foundWords = []
  theirNumbers = []

  for word in currentChat.words:
    if word.text in args:
      foundWords.append(word.text)
      theirNumbers.append(word.sentTimes)


  if not foundWords:
    bot.send_message(chatID, message.replies.fw[1])
  else:
    for part in stringForStats(chatID, foundWords, theirNumbers):
      bot.send_message(chatID, part)
