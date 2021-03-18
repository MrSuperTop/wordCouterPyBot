# # ? Imports
from config import bot, commands


# * Command itself
@bot.message_handler(commands=[commands['h']])
def sendHelpMessage(message):
  bot.send_message(message.chat.id, message.replies.help)
