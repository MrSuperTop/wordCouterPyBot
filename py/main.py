import telebot
from telebot import types

import config
from config import allCommands

from funStuff import *
from helpFuncs import *

import json
import os

bot = config.telebot

words = wordsNumbers = []
allWords = []
allWordsNumbers = []
languageSettings = {}

topWordIndex = globalTopWordIndex = allSendMessages = allSendWords = chatIdToUse = allInfo = 0
savedMessageID = -1
allContent = {}

# Functions

def stringInStatsView (words, wordsNumbers, addAdditionalInfo):
  if (words != []):
    wordWrittenTimes = 1
    toSendArray = []

    while (wordWrittenTimes <= max (wordsNumbers)):
      result = [allContent ['allStrings'] ['s'] [3] + str (wordWrittenTimes) + allContent ['allStrings'] ['tw'] [2]]
      for i in range (len (words)):
        if (wordWrittenTimes == wordsNumbers [i]):
          result.append ("'" + words [i] + "'")

      wordWrittenTimes += 1
      if (len (result) != 1):
        toSendArray.append (result)

    toSendAll = []
    for i in range (len (toSendArray)):
      toSendAll.append (str (toSendArray [i] [0]) + '\n' + ', '.join (toSendArray [i] [slice (1, len (toSendArray [i]))]) + '\n')

    if (addAdditionalInfo):
      toSendAll.append (allContent ['allStrings'] ['s'] [0]
      + str (allSendMessages) + allContent ['allStrings'] ['s'] [1]
      + str (allSendWords) + allContent ['allStrings'] ['s'] [2])

    return '\n'.join (toSendAll)

def updateAllInfo (message):
  chatIdToUse = str (message.chat.id)
  whereToSave = allInfo [chatIdToUse]

  whereToSave [0] = words
  whereToSave [1] = wordsNumbers
  whereToSave [2] = topWordIndex
  whereToSave [3] = allSendMessages
  whereToSave [4] = allSendWords

def saveChanges (clear = False):
  fileForBackup = open (config.txtPathes [0], 'w')
  fileForBackup.writelines ([json.dumps (allInfo, ensure_ascii = False) + '\n', json.dumps ([allWords, allWordsNumbers, globalTopWordIndex], ensure_ascii = False)])
  fileForBackup.close ()

def loadFromBackupFile (readFromFile):
  global allInfo, allWords, allWordsNumbers, globalTopWordIndex

  allInfo = json.loads (readFromFile [0])
  allWords = json.loads (readFromFile [1]) [0]
  allWordsNumbers = json.loads (readFromFile [1]) [1]
  globalTopWordIndex = json.loads (readFromFile [1]) [2]

def readLeng (chatIdToUse):
  fileForBackup = open (config.txtPathes [1], 'r')
  readFromFile = fileForBackup.read ()
  fileForBackup.close ()

  if (readFromFile == ''):
    languageSettings [chatIdToUse] = 'eng'
    allContent ['allStrings'] = config.allContentEng ['allStrings']

    fileForBackup = open (config.txtPathes [1], 'w')
    fileForBackup.write (json.dumps (languageSettings))
    fileForBackup.close ()
  else:
    readFromFile = json.loads (readFromFile)

  if (chatIdToUse in readFromFile):
    return readFromFile [chatIdToUse]
  else:
    readFromFile [chatIdToUse] = 'eng'
    return readFromFile [chatIdToUse]

def addDeleteInlineKeyboard (message, commandName, toSendMessageText, chatIDtoSend, additionalBtn  = None):
  markup = types.InlineKeyboardMarkup (row_width = 1)
  deleteBtn1 = types.InlineKeyboardButton (allContent ['allStrings'] ['skeyboard'] [1], callback_data = 'deleteMessage')
  deleteBtn2 = types.InlineKeyboardButton (allContent ['allStrings'] ['skeyboard'] [2] + '/' + commandName
  + allContent ['allStrings'] ['skeyboard'] [3], callback_data = 'deleteMessageAndCommand')

  if (additionalBtn != None):
    markup.add (deleteBtn1, deleteBtn2, additionalBtn)
  else:
    markup.add (deleteBtn1, deleteBtn2)
  bot.send_message (chatIDtoSend, toSendMessageText, reply_markup = markup)

def findWords (wordsToFind):
  if (', ' in wordsToFind or ' ' in wordsToFind):
    wordsToFind = splitSentence (wordsToFind)
  elif (',' in wordsToFind and not (' ' in wordsToFind)):
    wordsToFind = wordsToFind.split (',')
  elif ('.' in wordsToFind and not (' ' in wordsToFind)):
    wordsToFind = wordsToFind.split ('.')

  toSend = []
  allIndexes = []

  for word in wordsToFind:
    if (word in words):
      wordIndex = words.index (word)
      toSend.append (words [wordIndex])
      allIndexes.append (wordIndex)

  return stringInStatsView (toSend, allIndexes, False)

def initAllInfo (msg):
  global words, wordsNumbers, topWordIndex, allSendMessages, allSendWords, allInfo, chatIdToUse, allWords, allWordsNumbers, globalTopWordIndex, allContent

  chatIdToUse = str (msg.chat.id)
  readFromFile = readLeng (chatIdToUse)

  if (readFromFile != {}):
    if (readFromFile == 'ru'):
      allContent = config.allContentRu
    elif (readFromFile == 'eng'):
      allContent = config.allContentEng
  else:
    if (readFromFile == 'ru'):
      allContent = config.allContentRu
    elif (readFromFile == 'eng'):
      allContent = config.allContentEng
    else:
      allContent = config.allContentEng

  if (allInfo == 0):
    fileForBackup = open (config.txtPathes [0], 'r')
    readFromFile = fileForBackup.readlines ()
    fileForBackup.close ()

    if (readFromFile != []):
      loadFromBackupFile (readFromFile)
    else:
      allInfo = {chatIdToUse: [[], [], 0, 0, 0]}

  if (not (chatIdToUse in allInfo)):
    allInfo [chatIdToUse] = [[], [], 0, 0, 0]

  if (allInfo != 0):
    words = allInfo [chatIdToUse] [0]
    wordsNumbers = allInfo [chatIdToUse] [1]
    topWordIndex = allInfo [chatIdToUse] [2]
    allSendMessages = allInfo [chatIdToUse] [3]
    allSendWords = allInfo [chatIdToUse] [4]

# Main code

@bot.message_handler (commands = ['start'])
def start (message):
  global chatIdToUse, allInfo
  initAllInfo (message)

  bot.send_sticker (message.chat.id, config.greetingStickerId)
  bot.send_message (message.chat.id, allContent ['allStrings'] ['hi'] [0] + message.from_user.first_name + allContent ['allStrings'] ['hi'] [1] + bot.get_me ().username + allContent ['allStrings'] ['hi'] [2])

@bot.message_handler (commands = [allCommands ['h']])
def sendHelpMessage (message):
  initAllInfo (message)

  addDeleteInlineKeyboard (message, allCommands ['h'], allContent ['helpMessage'], message.chat.id, None)

@bot.message_handler (commands = [allCommands ['s']])
def sendStats (message):
  initAllInfo (message)

  keyboardItem1 = types.InlineKeyboardButton (allContent ['allStrings'] ['skeyboard'] [0], callback_data = 'toClearTrue')

  if (words != []):
    addDeleteInlineKeyboard (message, allCommands ['s'], stringInStatsView (words, wordsNumbers, True), message.chat.id, keyboardItem1)
  else:
    bot.send_message (message.chat.id, allContent ['allStrings'] ['nos'])

@bot.message_handler (commands = [allCommands ['tw']])
def sendTopWord (message):
  initAllInfo (message)

  if (wordsNumbers != []):
    toSend = (allContent ['allStrings'] ['tw'] [0] + 
    words [topWordIndex] + allContent ['allStrings'] ['tw'] [1] + 
    str (wordsNumbers [topWordIndex]) + allContent ['allStrings'] ['tw'] [2])

    addDeleteInlineKeyboard (message, allCommands ['tw'], toSend, message.chat.id)
  else:
    bot.send_message (message.chat.id, allContent ['allStrings'] ['nos'])

@bot.message_handler (commands = [allCommands ['gtw']])
def sendGlobalTopWord (message):
  initAllInfo (message)

  if (allWordsNumbers != []):
    bot.send_message (message.chat.id, allContent ['allStrings'] ['gtw'] + allWords [globalTopWordIndex] + allContent ['allStrings'] ['tw'] [1] + str (allWordsNumbers [globalTopWordIndex]) + allContent ['allStrings'] ['tw'] [2])
  else:
    bot.send_message (message.chat.id, allContent ['allStrings'] ['nos'])

@bot.message_handler (commands = [allCommands ['cs']])
def clearStats (message):
  global allWords, allWordsNumbers, globalTopWordIndex, allInfo
  initAllInfo (message)

  whatWillBeDeleted = allInfo [str (message.chat.id)]
  del allInfo [str (message.chat.id)]

  for i in range (len (whatWillBeDeleted [0])):
    word = whatWillBeDeleted [0] [i]
    wordWrittenTimes = whatWillBeDeleted [1] [i]
    wordIndex = allWords.index (word)

    if (word in allWords):
      if (allWordsNumbers [wordIndex] == wordWrittenTimes):
        del allWordsNumbers [wordIndex]
        del allWords [wordIndex]
      else:
        allWordsNumbers [wordIndex] -= wordWrittenTimes

  topWordIndex = 0

  for word in allWords:
    if (allWordsNumbers [topWordIndex] <= allWordsNumbers [allWords.index (word)]):
      globalTopWordIndex = allWords.index (word)

  saveChanges ()

  bot.send_message (message.chat.id, allContent ['allStrings'] ['sclrd'])

@bot.message_handler (commands = [allCommands ['sl']])
def sendLangSelector (message):
  initAllInfo (message)

  readFromFile = readLeng (chatIdToUse)

  markup = types.InlineKeyboardMarkup (row_width = 2)
  if (readFromFile == 'ru'):
    keyboardItem1 = types.InlineKeyboardButton ('Ru 🇷🇺 ✅', callback_data = 'setLengRu')
    keyboardItem2 = types.InlineKeyboardButton ('Eng 🇬🇧', callback_data = 'setLengEng')
  else:
    keyboardItem1 = types.InlineKeyboardButton ('Ru 🇷🇺', callback_data = 'setLengRu')
    keyboardItem2 = types.InlineKeyboardButton ('Eng 🇬🇧 ✅', callback_data = 'setLengEng')
  markup.add (keyboardItem1, keyboardItem2)

  bot.send_message (message.chat.id, allContent ['allStrings'] ['sectl'] [0], reply_markup = markup)

@bot.message_handler (content_types = ['text'])
def countWords (message):
  global topWordIndex, globalTopWordIndex, allSendMessages, allSendWords, chatIdToUse, allInfo, savedMessageID
  initAllInfo (message)

  if ('/' + allCommands ['fw'] in message.text and message.text [0:10] == '/' + allCommands ['fw']):
    if (not ('@' in message.text)):
      wordsToFind = message.text [11:len (message.text)]
    else:
      wordsToFind = message.text [12 + len (bot.get_me ().username):len (message.text)]

    toSend = findWords (wordsToFind)

    if (len (toSend) >= 1):
      bot.send_message (message.chat.id, toSend)
    else:
      bot.send_message (message.chat.id, allContent ['allStrings'] ['fw'] [2])
  
  elif ('/' + allCommands ['gfw'] in message.text and message.text [0:17] == '/' + allCommands ['gfw']):
    if (not ('@' in message.text)):
      wordsToFind = message.text [18:len (message.text)]
    else:
      wordsToFind = message.text [19 + len (bot.get_me ().username):len (message.text)]

    toSend = findWords (wordsToFind)

    if (len (toSend) >= 1):
      bot.send_message (message.chat.id, toSend)
    else:
      bot.send_message (message.chat.id, allContent ['allStrings'] ['fw'] [2])
  
  elif ('/' in message.text):
    bot.send_message (message.chat.id, allContent ['allStrings'] ['cnf'])

  elif (message.text == config.toGetStats and message.chat.id == config.ownerChatID):
    savedMessageID = message.message_id

    markup = types.InlineKeyboardMarkup (row_width = 1)
    keyboardItem1 = types.InlineKeyboardButton ('Write 🖊️', callback_data = 'writeFile')
    keyboardItem2 = types.InlineKeyboardButton ('Read 📖', callback_data = 'readFile')
    keyboardItem3 = types.InlineKeyboardButton ('Clear 🧽', callback_data = 'clearFile')

    markup.add (keyboardItem1, keyboardItem2, keyboardItem3)
    bot.send_message (config.ownerChatID, 'Что делать с информацией в файле textBackup.txt?', reply_markup = markup)

  elif (savedMessageID != -1 and int (savedMessageID) + 3 == message.message_id):
    fileForBackup = open (config.txtPathes [0], 'w')
    toWrite = message.text.split ('\n')

    if (len (toWrite) == 3):
      fileForBackup.writelines ([toWrite [0] + '\n', toWrite [2]])
      fileForBackup.close ()

      fileForBackup = open (config.txtPathes [0], 'r')
      readFromFile = fileForBackup.readlines ()
      fileForBackup.close ()

      loadFromBackupFile (readFromFile)
      bot.delete_message (message.chat.id, message.message_id - 1)
      bot.send_message (config.ownerChatID, 'Записано!')
    else:
      bot.send_message (config.ownerChatID, 'Что-то не так с тесктом, пропробуйте ещё раз...')

  elif (not ('http' in message.text)):
    splitedMessage = splitSentence (message.text)
    initAllInfo (message)

    if (not ('' in splitedMessage)):
      allSendWords += len (splitedMessage)
      allSendMessages += 1

      wordsAllToLower = allArrayToLowercase (words)

      for word in splitedMessage:
        wordLower = word.lower ()

        if (not (wordLower in wordsAllToLower)):
          words.append (word)
          wordsNumbers.append (1)
        else:
          wordsNumbers [wordsAllToLower.index (wordLower)] += 1

        wordsAllToLower = allArrayToLowercase (words)

        if (wordsNumbers [topWordIndex] <= wordsNumbers [wordsAllToLower.index (wordLower)]):
          topWordIndex = wordsAllToLower.index (wordLower)

        # Global part


        if (not (wordLower in allArrayToLowercase (allWords))):
          allWords.append (word)
          allWordsNumbers.append (1)
        else:
          allWordsNumbers [allArrayToLowercase (allWords).index (wordLower)] += 1


        if (allWordsNumbers [globalTopWordIndex] <= allWordsNumbers [allArrayToLowercase (allWords).index (wordLower)]):
          globalTopWordIndex = allArrayToLowercase (allWords).index (wordLower)

        updateAllInfo (message)

    allInfo [chatIdToUse] [3] = allSendMessages
    allInfo [chatIdToUse] [4] = allSendWords

    if (int (savedMessageID) + 3 != message.message_id):
      saveChanges ()

@bot.callback_query_handler (func = lambda call: True)
def callbackInline (call):
  global chatIdToUse, languageSettings
  initAllInfo (call.message)

  if call.message:
    if (call.data == 'toClearTrue'):
        markup = types.InlineKeyboardMarkup (row_width = 1)
        keyboardItem1 = types.InlineKeyboardButton (allContent ['allStrings'] ['skeyboard'] [1], callback_data = 'deleteMessage')
        markup.add (keyboardItem1)

        bot.delete_message (call.message.chat.id, call.message.message_id - 1)
        bot.edit_message_text (chat_id = call.message.chat.id, message_id = call.message.message_id, text = call.message.text, reply_markup = markup)
        clearStats (call.message)
    if (call.data == 'deleteMessage'):
      bot.answer_callback_query (callback_query_id = call.id, show_alert = False, text = allContent ['allStrings'] ['notf'] [0])
      bot.delete_message (call.message.chat.id, call.message.message_id)
    if (call.data == 'deleteMessageAndCommand'):
      bot.answer_callback_query (callback_query_id = call.id, show_alert = False, text = allContent ['allStrings'] ['notf'] [1])
      bot.delete_message (call.message.chat.id, call.message.message_id)
      bot.delete_message (call.message.chat.id, call.message.message_id - 1)

    if (call.data == 'writeFile' or call.data == 'readFile'):
      bot.delete_message (call.message.chat.id, call.message.message_id)

    if (call.data == 'writeFile'):
      markup = types.InlineKeyboardMarkup (row_width = 1)
      keyboardItem1 = types.InlineKeyboardButton ('Отмена ❌', callback_data = 'cancelWriteOrRead')
      markup.add (keyboardItem1)

      bot.send_message (config.ownerChatID, 'Жду то, что надо записать в файл...', reply_markup = markup)
      bot.delete_message (call.message.chat.id, savedMessageID)
    if (call.data == 'readFile'):
      fileForBackup = open (config.txtPathes [0], 'r')
      readFromFile = fileForBackup.readlines ()

      if (len (readFromFile) >= 2):
        bot.send_message (config.ownerChatID, readFromFile [0] + '\n' + readFromFile [1])
      else:
        bot.send_message (config.ownerChatID, 'Статиститки нет... 😥')
      fileForBackup.close ()
      bot.delete_message (call.message.chat.id, savedMessageID)
      bot.answer_callback_query (callback_query_id = call.id, show_alert = False, text = "Прочитано!")
    if (call.data == 'clearFile'):
      fileForBackup = open (config.txtPathes [0], 'w')
      fileForBackup.write ('')
      fileForBackup.close ()
      bot.delete_message (call.message.chat.id, savedMessageID)
      bot.delete_message (call.message.chat.id, savedMessageID + 1)
      bot.answer_callback_query (callback_query_id = call.id, show_alert = False, text = "Очищено!")
    if (call.data == 'cancelWriteOrRead'):
      bot.delete_message (call.message.chat.id, call.message.message_id)
      bot.answer_callback_query (callback_query_id = call.id, show_alert = False, text = "Действие отменено!")

    if (call.data == 'setLengRu'):
      chatIdToUse = str (call.message.chat.id)
      languageSettings [chatIdToUse] = 'ru'
      allContent ['allStrings'] = config.allContentRu ['allStrings']

      fileForBackup = open (config.txtPathes [1], 'w')
      fileForBackup.write (json.dumps (languageSettings))
      fileForBackup.close ()

      bot.delete_message (call.message.chat.id, call.message.message_id)
      bot.send_message (call.message.chat.id, allContent ['allStrings'] ['sectl'] [1])
    if (call.data == 'setLengEng'):
      chatIdToUse = str (call.message.chat.id)
      languageSettings [chatIdToUse] = 'eng'
      allContent ['allStrings'] = config.allContentEng ['allStrings']

      fileForBackup = open (config.txtPathes [1], 'w')
      fileForBackup.write (json.dumps (languageSettings))
      fileForBackup.close ()

      bot.delete_message (call.message.chat.id, call.message.message_id)
      bot.send_message (call.message.chat.id, allContent ['allStrings'] ['sectl'] [1])

bot.polling (none_stop = True)