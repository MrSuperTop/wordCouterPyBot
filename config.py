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
  's': 'stats',
  'cs': 'clear_stats',
  'stg': 'settings',
  'sl': 'lang',
  'h': 'help'
})

# * Diffrent languages strings for bot replies
replies = dotdict({
  'eng': dotdict({
    'help': '''
<b>Commands list:</b>\n
/{} - displays the word, which has been written the most times in your chat.
/{} - displays the word, which has been written the most times in all chats.\n
/{} (word) - displays local statistic about the word which is written instead of "(word)" can be written in format of "(word, word, word, word)" or "(word word word word)", (there can be unlimited number of words).\n
/{} - display all statistics about words for all time and displays number of send messages and words.
/{} - clears the stats.\n
/{} - set settings. You can turn on/off them and set values. More ditailed inforamtion about each setting is accesible through bot response.\n
/{} - set language.
/{} - sends this message.
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
    'notf': ['Message is deleted!', 'Message and a command was deleted!'],
    'sectl': ['Select lenguage.', 'English language is set!'],
    'cnf': 'Command is not found... 😥. Type "/help" for commands list.',
    'stg': dotdict({
      'msgTitle': 'Here you can set your settings',
      'valueSet': 'Value set!',
      'editButtonValue': 'To change settings values ⚙.',
      'moreInfoButtonValue': 'To get more info press here 📰.',
      'success': 'Setting changed!',
      'moveToChat': 'To change settings you have to go to the DM: @{0}.',
      'editorMessage': 'Select a setting you want to edit:',
      'sendNewValue': 'Set new value for a selected setting.',
      'valueIsWrong': 'New value doesn\'t mach the requirments...',
      'changeSuccess': 'The value was updated!',

      'strings': [
        [['Send stats into private messsages', 'stgSendPrivate', False]],
        [['Auto delete previous bot responces, when {0} new were sent', 'stgRemoveAfter', True]]
      ],
      
      'additionalInfo': [
        '<b>Detailed inforamation about each individual setting</b>',
        '<i><b>{}</b></i> - If tured on will send /stats command response to direct messages, so only you will be able to see it. If you have a lot a of statistics in your chat I would suggest you to turn it on, so /stats messages won\'t "pollute" your chat.',
        '<i><b>{}</b></i> - If turned on bot will automaticly delete all its respones and commands. In the chat won\'t be anything left behind and if you look through previous messages and some spare stuff disturbs you I would advise you to turn it on and set its value of 10. It will allow to keep you chat history clean and easy to read for people how have fallen behind.'
      ]
    })
  }),
  
  'ru': dotdict({
    'help': '''
<b>Список команд</b>:\n
/{} - выводит слово, которое было написано самое большое количество раз в вашем чате.
/{} - выводит слово, которое было написано самое большое количество раз во всех чатах в которых есть данный чат-бот.\n
/{} (слово) - выводит локальную статистику по слову, которое написано вместо "(слово)" может быть написано в формате "(слово, слово, слово, слово), или "(слово слово слово слово)", (слов может бить от одного до бесконечности).\n
/{} - выводит статистику по всем словам и количество написаных за всё время сообщений и слов.
/{} - чистит локальную статистику.\n
/{} - изменить язык.
/{} - установить настройки. Можете включать/включать и изменять значение более детальная информация про каждую настройку доступна в сообщении, которые будут преслано.\n
/{} - отправляет это сообщение.
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
    'Слова для поиска не были предоставлены 😥, пожалуйста, предоставте слова после команды.'
  ],
  'notf': ['Сообщение удалено!', 'Сообщение и команда удалена!'],
  'sectl': ['Выберете язык.', 'Русский язык установлен!'],
  'cnf': 'Комана не найдена... 😥. Напишите "/help" для списка команд.',
  'stg': dotdict({
    'msgTitle': 'Тут можно выбрать настройки.',
    'valueSet': 'Значение установлено!',
    'buttonValue': 'Изменить значения настрек ⚙.',
    'success': 'Настройка изменена!',
    'moveToChat': 'Для изменения настроек вам нужно перейти в чат с ботом: @{0}.',
    'editorMessage': 'Выберете настроку, которую хотите изменить:',
    'sendNewValue': 'Отправте новое значение для выбраной настроки.',
    'valueIsWrong': 'Новое значение не удовлетворяет критерии...',
    'changeSuccess': 'Значение успешно обновлено!',

    'strings': [
        [['Оправляет статистику в личные сообщения', 'stgSendPrivate', False]],
        [['Автоматически удаляет старые ответы, когда {0} отравлено', 'stgRemoveAfter', True]]
      ]
    # 'noArgsPassed': 'Чтобы установить значение настройки нужно передать её название (одно из списка) и новое значение, которое должно отвечать требованиям...',
    # 'settingDoesNotExist': 'Такой настройки не существует...',
    # 'additionalInfo': [
    #   [
    #     'Удалять после',
    #     'Устанавливает количество ответов бота после которых начну удалятся старые. Помогает держать чат в чистоте. Значения могу быть диапазоне от 5 до 100.'
    #   ]
    # ]
  })
})
})

# * Putting command names into all help messages for all languages
commandNames = [command[1] for command in commands.items()]
for language, strings in replies.items():
  strings.help = strings.help.format(*commandNames)

# ? Strings needed to send responses to /settings command
# ? and function to get needed parts of the array

# * list
allSettingsCallbacks = []
allSettingsEditingCallbacks = []

for i, (_, languageReplies) in enumerate(replies.items()):
  for setting in languageReplies.stg.strings:
    for button in setting:
      button.append(decapitalize(button[1][3:]))
      if i >= 1:
        continue

      allSettingsCallbacks.append(button[1])
      allSettingsEditingCallbacks.append(button[1].replace('stg', 'edit'))

# * Callbacks for additional /settings message buttons
additionalButtonCallbacks = ['stgEditValues', 'stgMoreInfo']

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
specialSymbols = list("""!"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~""")
numbers = list(string.octdigits)
