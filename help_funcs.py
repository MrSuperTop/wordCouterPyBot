# ? Imports
from functools import reduce
from json import dumps
from string import Formatter, ascii_uppercase

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import letters, specialSymbols, additionalButtonCallbacks
from data_base import Chats
from language import Language

# from help_funcs import get

# ? Functions
# * Word spliting functions
def wordContains(word, checkArray):
  """
  Checks if a string contains atleast one
  caracter which is in checkArray
  """

  for char in word:
    if char in checkArray:
      return True
  return False

def extractArgs(messageText):
  """
  Gets a list of arguments of a telegram bot command
  from message.text atribute
  """

  return messageText.split()[1:]

def splitSentence (toSplit):
  """
  Gets only the words without punctuation,
  which contain atleast one letter (not only numbers)
  """

  result = []

  for char in toSplit:
    if char == '\n':
      result.append(' ')

    elif char not in specialSymbols:
      result.append(char)
  resultArray = (''.join(result)).split(' ')
  result = []

  for word in resultArray:
    if wordContains(word, letters):
      result.append(word)

  return result

def canFormat(string):
  """Checks if a format method will have any effect"""

  formatSpecialArgs = [tup[1] for tup in Formatter().parse(string) if tup[1] is not None]
  return bool(formatSpecialArgs)

def splitWhenUppercase(string):
  """'TestString' to ['Test', 'String']"""

  result = []
  lastIndex = 0

  for i, char in enumerate(string):
    if i and char in ascii_uppercase:
      result.append(string[lastIndex:i])
      lastIndex = i

  result.append(string[lastIndex:])
  return result

def settingForUser(string):
  """
  Allows to convert "testMessage" to "Test Message.
  Will be used to repsent settings names for a user in
  a better looking way.
  """

  return ' '.join([item.capitalize() for item in splitWhenUppercase(string)])

# * Stats functions
def stringForStats(chatID, words, wordNumbers, additionalInfo=False, chatName=None):
  """
  Returns a formated in a speial way string using all information
  bot has to use in /stats command and not only
  """

  if not words:
    return None

  wordWrittenTimes = 1
  result = []

  # * Creating an array of ceratiain format. It will look somethig like this
  # & [['Word(s), which was/were written 1 time(s).', '"first"'],
  # & ['Word(s), which was/were written 2 time(s).', '"second"']]

  while wordWrittenTimes <= max(wordNumbers):
    # * Skipping an iterations if we don't have words which where written this much times
    if wordWrittenTimes not in wordNumbers:
      wordWrittenTimes += 1
      continue

    # * Adds all info to the string, we get info from the DB
    oneLine = [Language(chatID).strs.s[1].format(wordWrittenTimes)]
    for i, word in enumerate(words):
      if wordWrittenTimes == wordNumbers[i]:
        oneLine.append (f'"{word}"')

    # * Adding one like of words which where written same number of times
    # * and incrementing the variable responcible for everything

    result.append(oneLine)
    wordWrittenTimes += 1

  messages = [[]]
  for item in result:
    messages[-1].append(item)

    if len(reduce(lambda a, b : ''.join(a) + ''.join(b), messages[-1])) >= 3000:
      messages.append([])

  # * Adding each to make a strings which will look something like this
  # & 'Word(s), which was/were written 1 time(s).\n"first"'

  allMessages = []

  for index, message in enumerate(messages):
    singleMessage = []

    if not chatName is None and not index:
      singleMessage.append(Language(chatID).strs.s[4].format(
        chatName
      ))

    for item in message:
      messageText = f'{item[0]}\n{", ".join(item[1:])}'
      singleMessage.append(messageText)
    allMessages.append(singleMessage)

  # * Making a string out of our array and adding more info to the string if we want to
  result = []
  currentChat = Chats.getChat(chatID)

  for message in allMessages:
    # * Checking if we need additional info and add it
    if message == allMessages[-1] and additionalInfo:
      message.append(Language(chatID).strs.s[0].format(
        currentChat.sentMessages,
        currentChat.sentWords
      ))

    # * Adding all together, to get a final result
    result.append('\n\n'.join(message))

  for i, item in enumerate(result):
    if len(item) >= 3000:
      del result[i]

      chuncks = []
      j = 0
      for j in range(0, len(item), item.index(',', j+2950) + 1):
        try:
          chuncks.append(item[0+j:item.index(',', j+2950) + 1])
        except Exception:
          chuncks.append(item[j - 1:])
        # string[0+i:length+string.index(',', i - 50)] for i in range(0, len(string), length)

      for j, chunk in enumerate(chuncks):
        result.insert(i + j, chunk)

  return result

# * Markup functions
def getDeleteMarkup(commandName, message, additionalBtn=None):
  """
  Return a inline-keyboard with 2 default buttons and 1 additional if provided.
  Default buttons will allow user to delete a message, which was sent by the command
  and to delete a commands itself plus the message it sent.
  """

  chatID = message.chat.id
  markup = InlineKeyboardMarkup(row_width = 1)

  button1 = InlineKeyboardButton(Language(chatID).strs.skeyboard[1], callback_data='deleteMessage')
  button2 = InlineKeyboardButton(
    Language(chatID).strs.skeyboard[2].format(commandName),
    callback_data=dumps(['deleteWithCommand', message.message_id])
  )

  markup.add(button1, button2)
  if additionalBtn:
    markup.add(additionalBtn)

  return markup

def getLanguageMarkup(currentLanguage):
  """
  Will return a inline keyboard markup for language
  selector with all implamented languages selector buttons
  """

  markup = InlineKeyboardMarkup(row_width = 2)
  if currentLanguage == 'ru':
    item1 = InlineKeyboardButton('Ru 🇷🇺 ✅', callback_data = 'setLangRu')
    item2 = InlineKeyboardButton('Eng 🇬🇧', callback_data = 'setLangEng')
  elif currentLanguage == 'eng':
    item1 = InlineKeyboardButton('Ru 🇷🇺', callback_data = 'setLangRu')
    item2 = InlineKeyboardButton('Eng 🇬🇧 ✅', callback_data = 'setLangEng')
  markup.add(item1, item2)

  return markup


def settingsMarkup(chatID):
  markup = InlineKeyboardMarkup()
  currentSettings = Chats.objects(ID=chatID).get().settings
  settingsStrings = Language(chatID).strs.stg.strings

  for index, setting in enumerate(currentSettings):

    # * Will stop the foop if we have already iterated through all settings.
    # * Has to be stopped because "settings" object contains not only settings values,
    # * but some additional info connected to /settings command

    if index >= len(settingsStrings):
      break

    isOnString = '❌'
    settingObject = currentSettings[setting]

    if isinstance(settingObject, bool) and settingObject:
      isOnString = '✅'
    elif isinstance(settingObject, dict) and settingObject['haveTo']:
      isOnString = '✅'

    # * Creaing and adding all buttons to the markup. Will create using 2D array in config
    newButtons = []
    for index, buttonInfo in enumerate(settingsStrings[index]):
      buttonText = buttonInfo[0]

      # * Formating button text if can be formated
      if canFormat(buttonText):
        buttonText = buttonText.format(settingObject['value'])

      tempButton = InlineKeyboardButton(
        f'{buttonText}',
        callback_data=buttonInfo[1],
      )

      if not index:
        tempButton = InlineKeyboardButton(
          f'{buttonText} {isOnString}',
          callback_data=buttonInfo[1]
        )

      newButtons.append(tempButton)

    markup.row(*newButtons)

  # ? Additional buttons
  buttonText = Language(chatID).strs.stg

  # * Editing button
  markup.row(InlineKeyboardButton(
    buttonText.editButtonValue,
    callback_data=additionalButtonCallbacks[0]
  ))

  # * Button to get more info
  markup.row(InlineKeyboardButton(
    buttonText.moreInfoButtonValue,
    callback_data=additionalButtonCallbacks[1]
  ))

    # tempButton = InlineKeyboardButton(
    #   f'{settingsStrings[index][0]} {isOnString}',
    #   callback_data=settingsStrings[index][1]
    # )

    # markup.add(tempButton)

  return markup
