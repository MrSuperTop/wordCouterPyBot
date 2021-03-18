# ? Imports
# from language import Language
import os
import string

import telebot
from dotenv import load_dotenv

# ? Getting all info from .env and creating help functions and classes
# * Getting token from enviroment file at creating a bot instace
load_dotenv('token.env')
token = os.getenv('TOKEN')
bot = telebot.TeleBot(token, num_threads=4)

# * Just the oposite of capitalize() function
def decapitalize(s: str) -> str:
  if not s:  # check that s is not empty string
    return s
  return s[0].lower() + s[1:]

# * Class is something like a replacement for dict, allows to access keys with dots
class dotdict(dict):
  """dot.notation access to dictionary attributes"""

  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

# ? Config strings
# * Commands
commands = dotdict({
  'tw': 'top_word',
  'gtw': 'global_top_word',
  'fw': 'find_word',
  'gfw': 'global_fint_word',
  's': 'stats',
  'cs': 'clear_stats',
  'h': 'help',
  'sl': 'lang',
  'stg': 'settings'
})

# * Diffrent languages strings for bot replies
replies = dotdict({
  'eng': dotdict({
    'help': '''
Commands list:\n
/top_word - displays the word, which has been written the most times in your chat.
/global_top_word - displays the word, which has been written the most times in all chats.\n
/find_word (word) - displays local statistic about the word which is written instead of "(word)" can be written in format of "(word, word, word, word)" or "(word word word word)", (there can be unlimited number of words).\n
/stats - display all statistics about words for all time and displays number of send messages and words.
/clear_stats - clears the stats.\n
/lang - set language.
/help - sends this message.
''',

    'hi': 'Hello, {0}! I am - {1}.\nFor futher information type "/{2}".\n<b>Here you can set language you prefer:</b>',
    'skeyboard': ['Clear stats? 🧽', 'Remove message? ❌', 'Remove message and the command: "{0}"? ❌'],
    's': [
      'Total was sent: {0} message(s) and {1} word(s).',
      'Word(s), which was/were written {0} time(s)',
      'You can see the statistics here @{0}',
      'You need to start the bot to recieve messages from it, so go to @{0} and press "start" button.',
      '<b>Statistics form chat "{0}"</b>',
      'Move back to the chat: @{0}'
    ],
    'nos': 'No stats... 😥',
    'tw': 'The most popular word in this chat is "{0}", it was written {1} time(s).',
    'gtw': 'The mose popular word in all chats is "{0}", it was written {1} time(s)',
    'sclrd': 'Stats are cleared! 🧽',
    'fw': [
      'Word "{0}" was written {1} time(s)',
      'Nothing found... 😥 Seems like you have written anything like that...',
      'No words to search for where provided 😥, please, provide some after the command'
    ],
    'notf': ["Message is deleted!", 'Message and a command was deleted!'],
    'sectl': ['Select lenguage.', 'English language is set!'],
    'cnf': 'Command is not found... 😥. Type "/help" for commands list.',
    'stg': 'Here you can set your settings'
  }),
  
  'ru': dotdict({
    'help': '''
Список команд:\n
/top_word - выводит слово, которое было написано самое большое количество раз в вашем чате.
/global_top_word - выводит слово, которое было написано самое большое количество раз во всех чатах в которых есть данный чат-бот.\n
/find_word (слово) - выводит локальную статистику по слову, которое написано вместо "(слово)" может быть написано в формате "(слово, слово, слово, слово), или "(слово слово слово слово)", (слов может бить от одного до бесконечности).\n
/stats - выводит статистику по всем словам и количество написаных за всё время сообщений и слов.
/clear_stats - чистит локальную статистику.\n
/lang - изменить язык.
/help - отправляет это сообщение.
''',

  'hi': 'Привет, {0}! Я - {1}.\nДля получения дополнительной информации напишите "/{2}".\nНиже вы можете выбрать предпочитаемый язык:',
  'skeyboard': ['Очистить статистику? 🧽', 'Удалить сообщение? ❌', 'Удалить сообщение и команду: "{0}" ? ❌'],
  's': [
    'Всего было отправлено {0} сообщен(ий/я) и {1} слов(a).',
    'Слов(о/а), котор(ое/ые) были написаны {0} раз.',
    'Статистику можно посмотреть тут: @{0}',
    'Вам нужно запустить бота, чтобы получать сообщения от него, перейдите сюда: @{0} и нажмите кнопку "Старт".',
    '<b>Статистика из чата "{0}"</b>',
    'Перейти назад в чат: @{0}'
  ],
  'nos': 'Статистики нет... 😥',
  'tw': 'Самое популярное слово в этом чате: "{0}", было написано {1} раз(a).',
  'gtw': 'Самое популярное слово во всех чатах: "{0}", было написано {1} раз(а).',
  'sclrd': 'Статистика очищена! 🧽',
  'fw': [
    'Слово "{0}" было написано {1} раз(a).', 
    'Ничего не найдено... 😥 Похоже, вы ничего такого не писали...',
    'Слова для поиска не были предоставлены 😥, пожалуйста, предоставте слова после команды'
  ],
  'notf': ['Сообщение удалено!', 'Сообщение и команда удалена!'],
  'sectl': ['Выберете язык.', 'Русский язык установлен!'],
  'cnf': 'Комана не найдена... 😥. Напишите "/help" для списка команд.',
  'stg': 'Тут можно выбрать настройки'
})
})

# * Settings

settingsStrings = [
  ['Send stats into private messsages', 'stgSendPrivate'],
  ['Auto delete previous bot responces, when X new were sent', 'stgRemoveAfter']
]
for setting in settingsStrings:
  setting.append(decapitalize(setting[1][3:]))

# for i, setting in enumerate(settingsStrings):
#   settingsStrings[i] = setting.append(decapitalize(setting[1][3:]))

# * Some variables and char sets
implamentedLanguages = [item[0] for item in replies.items()]
greetingStickerId = 'CAACAgIAAxkBAAEBLSJfL-axDAdGXuP3mF5J3g3Tfj9IAwACIgADTlzSKWF0vv5zFvwUGgQ'

def generateCharsArray(start=0, howManyChars=1):
  """Generates a range of chars, when you provide their range of codes"""

  result = []
  for i in range(howManyChars):
    result.append(chr(i + start))
  return result


letters = [
  *list(string.ascii_letters),
 *generateCharsArray(1040, 32), 'Ё', 'ё', *generateCharsArray(1072, 32)
]

letters += ' '
specialSymbols = list("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
numbers = list(string.octdigits)
