# ? Imports
import os
import telebot

from dotenv import load_dotenv

# * Getting token from enviroment file at creating a bot instace
load_dotenv('token.env')
token = os.getenv('TOKEN')
telebot = telebot.TeleBot(token)

allContentEng = {
  'helpMessage': '''
Commands list:\n
/top_word - displays the word, which has been written the most times in your chat.
/global_top_word - displays the word, which has been written the most times in all chats.\n
/find_word (word) - displays local statistic about the word which is written instead of "(word)" can be written in format of "(word, word, word, word)" or "(word word word word)", (there can be unlimited number of words).
/global_find_word (word) - displays global statistic about the word which is written instead of "(word)" can be written in format of "(word, word, word, word)" or "(word word word word)", (there can be unlimited number of words).\n
/stats - display all statistics about words for all time and displays number of send messages and words.
/clear_stats - clears the stats.\n
/lang - set language.
/help - sends this message.
''',

  'allStrings': {
    'hi': ['Hello, ', '! I am - ', '.'],
    'skeyboard': ['Clear stats? 🧽', 'Remove message? ❌', "Remove message and the command: '", "' ? ❌"],
    's': ['Total was sent: ', ' message(s) and ', ' word(s).', 'Word(s), which was/were written ', ' time(s)'],
    'nos': 'No stats... 😥',
    'tw': 'The most popular word in this chat is "{0}", it was written {1} time(s).',
    'gtw': 'The mose popular word in all chats is "{0}", it was written {1} time(s)',
    'sclrd': 'Stats are cleared! 🧽',
    'fw': ["This word '", "' Was written ", 'Word is not found... 😥'],
    'notf': ["Message is deleted!", 'Message and a command was deleted!'],
    'sectl': ['Select lenguage.', 'English language is set!'],
    'cnf': 'Command is not found... 😥',
  },
}

allContentRu = {
  'helpMessage': '''
Список команд:\n
/top_word - выводит слово, которое было написано самое большое количество раз в +вашем чате.
/global_top_word - выводит слово, которое было написано самое большое количество раз во всех чатах в которых есть данный чат-бот.\n
/find_word (слово) - выводит локальную статистику по слову, которое написано вместо "(слово)" может быть написано в формате "(слово, слово, слово, слово), или "(слово слово слово слово)", (слов может бить от одного до бесконечности).
/global_find_word (слово) - выводит глобальную статистику по слову, которое написано вместо "(слово)" может быть написано в формате "(слово, слово, слово, слово), или "(слово слово слово слово)", (слов может бить от одного до бесконечности).\n
/stats - выводит статистику по всем словам и количество написаных за всё время сообщений и слов.
/clear_stats - чистит локальную статистику.\n
/lang - изменить язык.
/help - отправляет это сообщение.
''',

  'allStrings': {
    'hi': ['Привет, ', '! Я - ', '.'],
    'skeyboard': ['Очистить статистику? 🧽', 'Удалить сообщение? ❌', "Удалить сообщение и команду: '", "' ? ❌"],
    's': ['Всего было отправлено: ', ' сообщен(ий/я) и ', ' слов(a).', 'Слов(о/а), котор(ое/ые) были написаны '],
    'nos': 'Статистики нет... 😥',
    'tw': 'Самое популярное слово в этом чате: "{0}", было написано {1} раз(a).',
    'gtw': "Самое популярное слово во всех чатах: '",
    'sclrd': 'Статистика очищена! 🧽',
    'fw': ["Слово '", "' было написано ", 'Слово не найдено... 😥'],
    'notf': ["Сообщение удалено!", 'Сообщение и команда удалена!'],
    'sectl': ['Выберете язык.', 'Русский язык установлен!'],
    'cnf': 'Комана не найдена... 😥',
  },
}

allCommands = {
  'tw': 'top_word',
  'gtw': 'global_top_word',
  'fw': 'find_word',
  'gfw': 'global_fint_word',
  's': 'stats',
  'cs': 'clear_stats',
  'h': 'help',
  'sl': 'lang',
}

greetingStickerId = 'CAACAgIAAxkBAAEBLSJfL-axDAdGXuP3mF5J3g3Tfj9IAwACIgADTlzSKWF0vv5zFvwUGgQ'
toGetStats = 'ijAITem1l2XR9KspoGZLfwGfsKUvswLyP3zZM6B1cdPEM1hBPoDXnxcUa8RF7CIl'
txtPathes = ['./txt/textBackup.txt', './txt/lengSettingsInChats.txt']
ownerChatID = 726867610

def generateCharsArray (start=0, howManyChars=1):
  """Generates a range of chars, when you provide their range of codes"""

  result = []
  for i in range (howManyChars):
    result.append (chr (i + start))
  return result

letters = generateCharsArray (65, 26)
letters.extend(generateCharsArray (97, 26))
letters.extend(generateCharsArray (1040, 32))
letters.extend(generateCharsArray (1072, 32))
letters += ' '

numbers = generateCharsArray (48, 10)
