# ? Imports
from config import bot, commands
from help_funcs import getLanguageMarkup
from language import Language


# * Command
@bot.message_handler(commands=[commands['sl']])
def sendLangSelector(message):
  """
  Will send a message with inline keyboard, where user 
  can select language among supported once, when handled 
  selected language will be save in the database.
  """

  chatID = message.chat.id
  language = Language(chatID)

  selectorKeyboard = getLanguageMarkup(language.lang)
  bot.send_message(chatID, language.strs.sectl[0], reply_markup=selectorKeyboard)
