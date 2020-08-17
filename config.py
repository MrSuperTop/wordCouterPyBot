token = '1070345881:AAEkT33O7u0jkXU7NQr4qDHl9tTtkV75sIo'

allContentEng = {
  'helpMessage': '''
Commands list:\n
/top_word - displays the word, which has been written the most times in your chat.
/global_top_word - displays the word, which has been written the most times in all chats.\n
/find_word (word) - displays local statistic about the word which is written instead of "(word)".
/global_find_word (word) - displays global statistic about the word which is written instead of "(word)".\n
/stats - display all statistics about words for all time and displays number of send messages and words.
/clear_stats - clears the stats.\n
/help - sends this message.
''',

  'allStrings': {
    'hi': ['Hello, ', '! I am - ', '.'],
    'skeyboard': ['Clear stats? 🧽', 'Remove message? ❌'],
    's': ['Total was sent: ', ' message(s) and ', ' word(s).'],
    'nos': 'No stats... 😥',
    'tw': ["The most popular word in this chat is: '", "', it was written: ", ' time(s).'],
    'gtw': "The mose popular word in all chats: '",
    'sclrd': 'Stats is cleared! 🧽',
    'fw': ["This word '", "' Was written ", 'Word is not found... 😥'],
    'notf': ["Message is deleted!"],
    'sectl': ['Select lenguage.', 'English language is set!'],
  },
}

allContentRu = {
  'helpMessage': '''
Список команд:\n
/top_word - выводит слово, которое было написано самое большое количество раз в вашем чате.
/global_top_word - выводит слово, которое было написано самое большое количество раз во всех чатах в которых есть данный чат-бот.\n
/find_word (слово) - выводит локальную статистику по слову, которое написано вместо "(слово)".
/global_find_word (слово) - выводит глобальную статистику по слову, которое написано вместо "(слово)".\n
/stats - выводит статистику по всем словам и количество написаных за всё время сообщений и слов.
/clear_stats - чистит локальную статистику.\n
/help - отправляет это сообщение.
''',

  'allStrings': {
    'hi': ['Привет, ', '! Я - ', '.'],
    'skeyboard': ['Очистить статистику? 🧽', 'Удалить сообщение? ❌', "Удалить сообщение и команду: '", "' ? ❌"],
    's': ['Всего было отправлено: ', ' сообщений(я) и ', ' слов(a).', 'Слова(о), которые были написаны '],
    'nos': 'Статистики нет... 😥',
    'tw': ["Самое популярное слово в этом чате: '", "', было написано: ", ' раз(a).'],
    'gtw': "Самое популярное слово во всех чатах: '",
    'sclrd': 'Статистика очищена! 🧽',
    'fw': ["Слово '", "' было написано ", 'Слово не найдено... 😥'],
    'notf': ["Сообщение удалено!", 'Сообщение и команда удалена!'],
    'sectl': ['Выберете язык.', 'Русский язык установлен!'],
  },
}

greetingStickerId = 'CAACAgIAAxkBAAEBLSJfL-axDAdGXuP3mF5J3g3Tfj9IAwACIgADTlzSKWF0vv5zFvwUGgQ'
toGetStats = 'IRiIaFGN8f}dIPh/.z,GMYA2N>LJ_jz?C,<<p@3Y(`7,~7ff==s_q0Cj}LG&Z:u'
ownerChatID = 726867610

allCommands = {
  'tw': 'top_word',
  'gtw': 'global_top_word',
  'fw': 'find_word',
  'gfw': 'global_fint_word',
  's': 'stats',
  'cs': 'clear_stats',
  'h': 'help',
  'sl': 'set_leng',
}

def generateCharsArray (start, howManyChars):
	result = []
	for i in range (howManyChars):
		result.append (chr (i + start))
	return result

letters = generateCharsArray (65, 26)
letters.extend(generateCharsArray (97, 26))
letters.extend(generateCharsArray (1040, 32))
letters.extend(generateCharsArray (1072, 32))
letters += ' '