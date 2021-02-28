
# ? Imports
# * Built-in modules
import json

# * Telegram Liblary
from telebot import types

# * Config
import config
from config import allCommands

# * Local files
from fun_stuff import *
from help_funcs import *

# * Modules needed to work with mongoDB
from data_base import Word, Chats

# ? Commands
# from os.path import dirname, basename, isfile, join
# import glob
# modules = glob.glob(join(dirname(__file__), "commands/*.py"))
# __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
# from commands.start import *

bot = config.telebot

topWordIndex = globalTopWordIndex = allSendMessages = allSendWords = chatIdToUse = allInfo = 0
savedMessageID = -1
allContent = {}

# * Functions

def stringInStatsView(chatID, additionalInfo):
  """Returns a formated string using all information bot has to use in /stats command and not only"""

  currentChat = Chats.objects(ID=chatID).get()
  words = currentChat.words
  wordNumbers = [word.sentTimes for word in words]

  if words != []:
    wordWrittenTimes = 1
    result = []

    # * Creating an array of ceratiain format. It will look somethig like this
    # & [['Word(s), which was/were written 1 time(s).', '"first"'],
    # & ['Word(s), which was/were written 2 time(s).', '"second"']]

    while wordWrittenTimes <= max(wordNumbers):
      # * Skipping an iterations if we don't have words which where written this much times
      if not wordWrittenTimes in wordNumbers:
        wordWrittenTimes += 1
        continue

      # * Adds all info to the string, we get info from the DB
      oneLine = [allContent['allStrings']['s'][3] + str(wordWrittenTimes) + allContent['allStrings']['s'][4]]
      for i, word in enumerate(words):
        if wordWrittenTimes == wordNumbers[i]:
          oneLine.append (f'"{word.text}"')

      result.append(oneLine)
      wordWrittenTimes += 1

    # * Making a string out of our array
    stringResult = []
    for item in result:
      stringResult.append(f'{item[0]}\n{", ".join(item[1:])}')

    currentChat = Chats.objects(ID=chatID).get()
    if additionalInfo: # ! Has to be modified
      stringResult.append(allContent['allStrings']['s'][0]
      + str(currentChat.sentMessages) + allContent['allStrings']['s'][1]
      + str(currentChat.sentWords) + allContent['allStrings']['s'][2])

    stringResult = '\n\n'.join(stringResult)
    return stringResult

def checkChat(chatID):
  """Checks if the chat exists in the database,
  if doesn't fills it with basic placeholder info
  and saves it to the database"""

  try:
    Chats.objects(ID=chatID).get()
  except Chats.DoesNotExist:
    print('\n', "There is no chats with id like this!", '\n')

    tempWord = Word(
      text = '',
      sentTimes = 1
    )

    Chats(
      language = "eng",
      ID = chatID,
      words = [],
      topWord = tempWord,
      sentWords = 0,
      sentMessages = 0
    ).save()

def setLang(chatID, language):
  """Sets language for a chat with provided ID and saves it to the DB"""

  currentChat = Chats.objects(ID=chatID).get()
  currentChat.language = language
  currentChat.save()

def getLang(chatID):
  """Gets the language of current chat from the file / DB"""

  try:
    return Chats.objects(ID=chatID).get().language
  except Chats.DoesNotExist:
    return 'eng'

def addDeleteInlineKeyboard(message, commandName, toSendMessageText, additionalBtn=None):
  chatIDtoSend = message.chat.id

  markup = types.InlineKeyboardMarkup(row_width = 1)
  deleteBtn1 = types.InlineKeyboardButton(allContent['allStrings']['skeyboard'][1], callback_data='deleteMessage')
  deleteBtn2 = types.InlineKeyboardButton(allContent['allStrings']['skeyboard'][2] + '/' + commandName
  + allContent['allStrings']['skeyboard'][3], callback_data='deleteMessageAndCommand')

  if (additionalBtn != None):
    markup.add(deleteBtn1, deleteBtn2, additionalBtn)
  else:
    markup.add(deleteBtn1, deleteBtn2)
  bot.send_message(chatIDtoSend, toSendMessageText, reply_markup=markup)

# ! Don't remove
# def findWords(wordsToFind):
#   if (', ' in wordsToFind or ' ' in wordsToFind):
#     wordsToFind = splitSentence (wordsToFind)
#   elif (',' in wordsToFind and not (' ' in wordsToFind)):
#     wordsToFind = wordsToFind.split (',')
#   elif ('.' in wordsToFind and not (' ' in wordsToFind)):
#     wordsToFind = wordsToFind.split ('.')

#   toSend = []
#   allIndexes = []

#   for word in wordsToFind:
#     if (word in words):
#       wordIndex = words.index(word)
#       toSend.append(words[wordIndex])
#       allIndexes.append(wordIndex)

#   return stringInStatsView(toSend, allIndexes, False)

def fetchStrings():
  global allContent

  language = getLang(chatIdToUse)

  if (language != {}):
    if (language == 'ru'):
      allContent = config.allContentRu
    elif (language == 'eng'):
      allContent = config.allContentEng
  else:
    if (language == 'ru'):
      allContent = config.allContentRu
    elif (language == 'eng'):
      allContent = config.allContentEng
    else:
      allContent = config.allContentEng

fetchStrings() # ! Has to be move to a more appropariate place or redo this

# Main code

@bot.message_handler(commands = ['start'])
def start(message):
  """Sends a greeting message from config file"""

  bot.send_sticker(message.chat.id, config.greetingStickerId)
  bot.send_message(message.chat.id, allContent['allStrings']['hi'][0] + message.from_user.first_name + allContent['allStrings']['hi'][1] + bot.get_me().username + allContent['allStrings']['hi'][2])

@bot.message_handler(commands = [allCommands['h']])
def sendHelpMessage(message):

  addDeleteInlineKeyboard(message, allCommands['h'], allContent['helpMessage'])

@bot.message_handler(commands = [allCommands['s']])
def sendStats(message):
  currentChat = Chats.objects(ID=message.chat.id).get()

  keyboardItem1 = types.InlineKeyboardButton(allContent['allStrings']['skeyboard'][0], callback_data = 'toClearTrue')

  if currentChat.words != []:
    addDeleteInlineKeyboard(message, allCommands['s'], stringInStatsView(message.chat.id, True), keyboardItem1)
  else:
    bot.send_message(message.chat.id, allContent['allStrings']['nos'])

@bot.message_handler(commands = [allCommands['tw']])
def sendTopWord(message):
  """Gets from the DB most commonly used word objects and sends it to the chat"""

  checkChat(message.chat.id)
  currentChat = Chats.objects(ID=message.chat.id).get()
  topWord = currentChat.topWord

  if topWord:
    toSend = allContent['allStrings']['tw'].format(topWord.text, topWord.sentTimes)

    addDeleteInlineKeyboard(message, allCommands['tw'], toSend)
  else:
    bot.send_message(message.chat.id, allContent['allStrings']['nos'])

@bot.message_handler(commands = [allCommands['gtw']])
def sendGlobalTopWord(message):
  checkChat(message.chat.id)
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

  resultString = allContent['allStrings']['gtw'].format(topWordText, sentEverywhere)
  print(topWordText, sentEverywhere)
  print(resultString)
  addDeleteInlineKeyboard(message, allCommands['gtw'], resultString)

@bot.message_handler(commands = [allCommands['cs']])
def clearStats(message):
  # * Cleaning the chat Document
  currentChat = Chats.objects(ID=message.chat.id).get()
  currentChat.words = []
  currentChat.sentMessages = currentChat.sentWords = 0
  currentChat.save()

  bot.send_message(message.chat.id, allContent['allStrings']['sclrd'])

@bot.message_handler(commands = [allCommands['sl']])
def sendLangSelector(message):
  language = getLang(message.chat.id)
  print(language)

  markup = types.InlineKeyboardMarkup(row_width = 2)
  if language == 'ru':
    keyboardItem1 = types.InlineKeyboardButton('Ru 🇷🇺 ✅', callback_data = 'setLangRu')
    keyboardItem2 = types.InlineKeyboardButton('Eng 🇬🇧', callback_data = 'setLangEng')
  else:
    keyboardItem1 = types.InlineKeyboardButton('Ru 🇷🇺', callback_data = 'setLangRu')
    keyboardItem2 = types.InlineKeyboardButton('Eng 🇬🇧 ✅', callback_data = 'setLangEng')
  markup.add(keyboardItem1, keyboardItem2)

  bot.send_message(message.chat.id, allContent['allStrings']['sectl'][0], reply_markup = markup)

@bot.message_handler(content_types=['text'])
def countWords(message):
  global savedMessageID

  if '/' + allCommands['fw'] in message.text and message.text[0:10] == '/' + allCommands['fw']:
    if not '@' in message.text :
      wordsToFind = message.text[11:len(message.text)]
    else:
      wordsToFind = message.text[12 + len(bot.get_me().username):len(message.text)]

    toSend = findWords(wordsToFind)

    if len(toSend) >= 1:
      bot.send_message(message.chat.id, toSend)
    else:
      bot.send_message(message.chat.id, allContent['allStrings']['fw'][2])
  elif '/' + allCommands['gfw'] in message.text and message.text[0:17] == '/' + allCommands['gfw']:
    if not '@' in message.text:
      wordsToFind = message.text[18:len(message.text)]
    else:
      wordsToFind = message.text[19 + len(bot.get_me().username):len(message.text)]

    toSend = findWords(wordsToFind)

    if len(toSend) >= 1:
      bot.send_message(message.chat.id, toSend)
    else:
      bot.send_message(message.chat.id, allContent['allStrings']['fw'][2])

  elif '/' in message.text:
    bot.send_message(message.chat.id, allContent['allStrings']['cnf'])

  elif (message.text == config.toGetStats and message.chat.id == config.ownerChatID):
    savedMessageID = message.message_id

    markup = types.InlineKeyboardMarkup(row_width = 1)
    keyboardItem1 = types.InlineKeyboardButton('Write 🖊️', callback_data = 'writeFile')
    keyboardItem2 = types.InlineKeyboardButton('Read 📖', callback_data = 'readFile')
    keyboardItem3 = types.InlineKeyboardButton('Clear 🧽', callback_data = 'clearFile')

    markup.add(keyboardItem1, keyboardItem2, keyboardItem3)
    bot.send_message(config.ownerChatID, 'Что делать с информацией в файле textBackup.txt?', reply_markup = markup)

  elif savedMessageID != -1 and int(savedMessageID) + 3 == message.message_id:
    fileForBackup = open(config.txtPathes[0], 'w')
    toWrite = message.text.split('\n')

    if len(toWrite) == 3:
      fileForBackup.writelines([toWrite[0] + '\n', toWrite[2]])
      fileForBackup.close()

      bot.delete_message(message.chat.id, message.message_id - 1)
      bot.send_message(config.ownerChatID, 'Записано!')
    else:
      bot.send_message(config.ownerChatID, 'Что-то не так с тесктом, пропробуйте ещё раз...')

  elif not 'http' in message.text:
    splitedMessage = splitSentence(message.text)

    if not '' in splitedMessage:
      # * Checking if current chat exists in the database an getting its object to use
      checkChat(message.chat.id)
      currentChat = Chats.objects(ID=message.chat.id).get()

      # * Update "counters" in database
      currentChat.sentWords += len(splitedMessage)
      currentChat.sentMessages += 1

      wordsList = []

      for part in splitedMessage:
        wordLower = part.lower()

        # * Adds a word in the list, if it's not fond in it
        wordsList = [word.text for word in currentChat.words]
        if not wordLower in wordsList or not currentChat.words:
          print('New word is created')

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
        wordsList = [word.text for word in currentChat.words]
        wordNumbers = [word.sentTimes for word in currentChat.words]

        topIndex = wordNumbers.index(max(wordNumbers))
        tempWord = Word(
          text = wordsList[topIndex],
          sentTimes = max(wordNumbers)
        )

        currentChat.topWord = tempWord

        # * Saving all changes
        currentChat.save()

    if int(savedMessageID) + 3 != message.message_id:
      print('We are saving data to the DB')

@bot.callback_query_handler(func = lambda call: True)
def callbackInline(call):
  """Function to control inline buttonsm won't be used anywhere, just in the decorator"""

  global chatIdToUse, allContent

  if call.message:
    if call.data == 'toClearTrue':
      markup = types.InlineKeyboardMarkup(row_width = 1)
      keyboardItem1 = types.InlineKeyboardButton(allContent['allStrings']['skeyboard'][1], callback_data = 'deleteMessage')
      markup.add(keyboardItem1)

      bot.delete_message(call.message.chat.id, call.message.message_id - 1)
      bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = call.message.text, reply_markup = markup)
      clearStats(call.message)
    if call.data == 'deleteMessage':
      bot.answer_callback_query(callback_query_id = call.id, show_alert = False, text = allContent['allStrings']['notf'][0])
      bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == 'deleteMessageAndCommand':
      bot.answer_callback_query(callback_query_id = call.id, show_alert = False, text = allContent['allStrings']['notf'][1])
      bot.delete_message(call.message.chat.id, call.message.message_id)
      bot.delete_message(call.message.chat.id, call.message.message_id - 1)

    if call.data == 'writeFile' or call.data == 'readFile':
      bot.delete_message(call.message.chat.id, call.message.message_id)

    if call.data == 'writeFile':
      markup = types.InlineKeyboardMarkup(row_width = 1)
      keyboardItem1 = types.InlineKeyboardButton('Отмена ❌', callback_data = 'cancelWriteOrRead')
      markup.add(keyboardItem1)

      bot.send_message(config.ownerChatID, 'Жду то, что надо записать в файл...', reply_markup = markup)
      bot.delete_message(call.message.chat.id, savedMessageID)
    if call.data == 'readFile':
      fileForBackup = open(config.txtPathes[0], 'r')
      readFromFile = fileForBackup.readlines()

      if len(readFromFile) >= 2:
        bot.send_message(config.ownerChatID, readFromFile[0] + '\n' + readFromFile[1])
      else:
        bot.send_message(config.ownerChatID, 'Статиститки нет... 😥')
      fileForBackup.close()
      bot.delete_message(call.message.chat.id, savedMessageID)
      bot.answer_callback_query(callback_query_id = call.id, show_alert = False, text = "Прочитано!")
    if call.data == 'clearFile':
      fileForBackup = open(config.txtPathes[0], 'w')
      fileForBackup.write('')
      fileForBackup.close()
      bot.delete_message(call.message.chat.id, savedMessageID)
      bot.delete_message(call.message.chat.id, savedMessageID + 1)
      bot.answer_callback_query(callback_query_id = call.id, show_alert = False, text = "Очищено!")
    if call.data == 'cancelWriteOrRead':
      bot.delete_message(call.message.chat.id, call.message.message_id)
      bot.answer_callback_query(callback_query_id = call.id, show_alert = False, text = "Действие отменено!")

    chatID = call.message.chat.id

    if call.data == 'setLangRu':
      setLang(chatID, 'ru')
      allContent['allStrings'] = config.allContentRu['allStrings']

      bot.delete_message(chatID, call.message.message_id)

    if call.data == 'setLangEng':
      setLang(chatID, 'eng')
      allContent['allStrings'] = config.allContentEng['allStrings']

      bot.delete_message(chatID, call.message.message_id)

    bot.send_message(chatID, allContent['allStrings']['sectl'][1])

bot.polling(none_stop = True)
