# ? Imports
import config

# * Getting bot variable from config
bot = config.telebot

# ? Commands
@bot.message_handler (commands=['rasputin'])
def _ (message):
  bot.send_message (message.chat.id, 'https://youtu.be/YgGzAKP_HuM')

@bot.message_handler (commands=['crab'])
def _ (message):
  bot.send_message (message.chat.id, 'https://youtu.be/LDU_Txk06tM')
