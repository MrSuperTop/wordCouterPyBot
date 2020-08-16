import telebot
import config
import json
import os

bot = telebot.TeleBot (config.token)
words = wordsNumbers = []
allWords = []
allWordsNumbers = []
topWordIndex = globalTopWordIndex = allSendMessages = allSendWords = chatIdToUse = allInfo = 0

def saveChanges (clear = False):
  if ('topWordCouterBot' in list (os.listdir ('.'))):
    fileForBackup = open ('topWordCouterBot/textBackup.txt', 'w')
  else:
    fileForBackup = open ('textBackup.txt', 'w')
  fileForBackup.writelines ([json.dumps (allInfo) + '\n', json.dumps ([allWords, allWordsNumbers, globalTopWordIndex])])
  fileForBackup.close ()

def initAllInfo (msg):
  global words, wordsNumbers, topWordIndex, allSendMessages, allSendWords, allInfo, chatIdToUse, allWords, allWordsNumbers, globalTopWordIndex

  chatIdToUse = str (msg.chat.id)

  if (allInfo == 0):
    if ('topWordCouterBot' in os.listdir ('.')):
      fileForBackup = open ('topWordCouterBot/textBackup.txt', 'r')
    else:
      fileForBackup = open ('textBackup.txt', 'r')
    readFromFile = fileForBackup.readlines ()
    fileForBackup.close ()

    if (readFromFile != []):
      allInfo = json.loads (readFromFile [0])
      allWords = json.loads (readFromFile [1]) [0]
      allWordsNumbers = json.loads (readFromFile [1]) [1]
      globalTopWordIndex = json.loads (readFromFile [1]) [2]
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

@bot.message_handler (commands = ['start'])
def start (message):
  global chatIdToUse, allInfo
  initAllInfo (message)

  bot.send_sticker (message.chat.id, config.greetingStickerId)
  bot.send_message (message.chat.id, 'Привет, ' + message.from_user.first_name + '! Я - ' + bot.get_me ().username + '.')

@bot.message_handler (commands = ['help'])
def sendHelpMessage (message):
  bot.send_message (message.chat.id, config.helpMessage)

@bot.message_handler (commands = ['stats'])
def sendStats (message):
  initAllInfo (message)

  if (words != []):
    wordWrittenTimes = 1
    toSendArray = []

    while (wordWrittenTimes <= max (wordsNumbers)):
      result = [wordWrittenTimes]

      for i in range (len (words)):
        if (wordWrittenTimes == wordsNumbers [i]):
          result.append ("'" + words [i] + "'")

      wordWrittenTimes += 1
      if (len (result) != 1):
        toSendArray.append (result)

    toSendAll = []

    for i in range (len (toSendArray)):
      toSendAll.append (str (toSendArray [i] [0]) + '\n' + ', '.join (toSendArray [i] [slice (1, len (toSendArray [i]))]) + '\n')

    toSendAll.append ('Всего было отравлено: ' + str (allSendMessages) + ' сообщений(я) и ' + str (allSendWords) + ' слов(a).')

    bot.send_message (message.chat.id, '\n'.join (toSendAll))
  else:
    bot.send_message (message.chat.id, 'Статиститки нет... 😥')

@bot.message_handler (commands = ['top_word'])
def sendTopWord (message):
  initAllInfo (message)

  if (wordsNumbers != []):
    bot.send_message (message.chat.id, 'Самое популярное слово в этом чате: ' + "'" + words [topWordIndex] + "', было написано: " + str (wordsNumbers [topWordIndex]) + ' раз(a).')
  else:
    bot.send_message (message.chat.id, 'Статиститки нет... 😥')

@bot.message_handler (commands = ['global_top_word'])
def sendGlobalTopWord (message):
  initAllInfo (message)

  if (allWordsNumbers != []):
    bot.send_message (message.chat.id, 'Самое популярное слово во всех чатах: ' + "'" + allWords [globalTopWordIndex] + "', было написано: " + str (allWordsNumbers [globalTopWordIndex]) + ' раз(a).')
  else:
    bot.send_message (message.chat.id, 'Статиститки нет... 😥')

@bot.message_handler (commands = ['clear_stats'])
def clearStats (message):
  global allWords, allWordsNumbers, globalTopWordIndex, allInfo
  initAllInfo (message)

  whatWillBeDeleted = allInfo [str (message.chat.id)]
  del allInfo [str (message.chat.id)]

  for i in range (len (whatWillBeDeleted [0])):
    word = whatWillBeDeleted [0] [i]
    wordWrittenTimes = whatWillBeDeleted [1] [i]

    if (word in allWords):
      if (allWordsNumbers [i] == wordWrittenTimes):
        del allWordsNumbers [i]
        del allWords [i]
      else:
        allWordsNumbers [i] -= wordWrittenTimes

  topWordIndex = 0

  if (allWordsNumbers != []):
    for word in allWords:
      if (allWordsNumbers [topWordIndex] < allWordsNumbers [allWords.index (word)]):
        topWordIndex = allWords.index (word)

  saveChanges ()

  bot.send_message (message.chat.id, 'Статистика очищена! 🧽')

# Fun

@bot.message_handler (commands = ['rasputin'])
def sendURL (message):
  bot.send_message (message.chat.id, 'https://youtu.be/YgGzAKP_HuM')

@bot.message_handler (content_types = ['text'])
def countWords (message):
  global topWordIndex, globalTopWordIndex, allSendMessages, allSendWords, chatIdToUse, allInfo
  initAllInfo (message)

  allSendMessages += 1

  if (not ('http' in message.text)):
    splitedMessage = message.text.split (' ')
    allSendWords += len (splitedMessage)

    for word in splitedMessage:
      if (not (word in words)):
        words.append (word)
        wordsNumbers.append (1)
      else:
        wordsNumbers [words.index (word)] += 1

      if (wordsNumbers [topWordIndex] < wordsNumbers [words.index (word)]):
        topWordIndex = words.index (word)

      # Global part

      if (not (word in allWords)):
        allWords.append (word)
        allWordsNumbers.append (1)
      else:
        allWordsNumbers [allWords.index (word)] += 1

      if (allWordsNumbers [globalTopWordIndex] < allWordsNumbers [allWords.index (word)]):
        globalTopWordIndex = allWords.index (word)

  allInfo [chatIdToUse] [3] = allSendMessages
  allInfo [chatIdToUse] [4] = allSendWords

  saveChanges ()

bot.polling (none_stop = True)