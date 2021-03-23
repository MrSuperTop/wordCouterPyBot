# ? Imports
from config import bot, commands, greetingStickerId
from help_funcs import getLanguageMarkup
from language import Language


# * Command
@bot.message_handler(commands = ['start'])
def start(message):
  """
  Sends a greeting message from config file
  and provides some basic bot configuration settings
  """

  chatID = message.chat.id

  language = Language(chatID).lang
  languageMarkup = getLanguageMarkup(language)

  bot.send_sticker(chatID, greetingStickerId)

  greetingString = message.replies.hi.format(
    message.from_user.first_name,
    bot.get_me().username,
    commands.h
  )

  bot.send_message(chatID, greetingString, reply_markup=languageMarkup, parse_mode='html')
