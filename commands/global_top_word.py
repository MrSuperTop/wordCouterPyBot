# ? Imports
from config import bot, commands
from data_base import Chats, Word
from help_funcs import getDeleteMarkup
from language import Language


# * Command
@bot.message_handler(commands = [commands.gtw])
def sendGlobalTopWord(message):
  # wordWritten = 0
  topWordText = ''

  # * Here will be saved the chat object which was most commonly used word,
  # * none of the words in other chats weren't sent as much times
  # * as particular word in this chat was.

  chatWithTop = Chats()

  # * Searches for the chat, which has the most used word in it
  # * (more ditailed description of it is written above the 'chatWithTop' variable defenition)

  sentTimes = 0
  while Chats.objects(words__sentTimes__gt=sentTimes):
    allMatching = Chats.objects(words__sentTimes__gt=sentTimes)
    if len(allMatching) == 1 or len(allMatching) == sentTimes + 2:
      chatWithTop = allMatching[0]
      topWordText = chatWithTop.topWord.text

      break
    sentTimes += 1

  # * Fooks for this word
  sentEverywhere = 0
  for chat in Chats.objects(words__text=topWordText):
    for word in chat.words:
      if word.text == topWordText:
        sentEverywhere += word.sentTimes

  resultString = Language(message).strs.gtw.format(topWordText, sentEverywhere)
  bot.send_message(message.chat.id, resultString, reply_markup=getDeleteMarkup(commands.gtw, message))
