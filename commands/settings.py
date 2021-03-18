# ? Imports0
from config import bot, commands, settingsStrings
from data_base import Chats, Settings
from help_funcs import settingsMarkup
from language import Language
from telebot.apihelper import ApiException


# * Command
@bot.message_handler(commands=[commands.stg])
def sendSettings(message):
  markup = settingsMarkup(message.chat.id)
  chatID = message.chat.id
  currentChat = Chats.getChat(message.chat.id)
  lastMessageID = currentChat.settings.lastMessageID

  # * Deleting previous "settings" message
  try:
    if lastMessageID:
      bot.delete_message(chatID, lastMessageID)
  except ApiException:
    pass

  # * Sending new one
  settingsMessage = bot.send_message(chatID, message.replies.stg, reply_markup=markup)

  # * Setting new messageID when the message was send to be able to delete this one,
  # * when new settings will be sent

  currentChat.settings.lastMessageID = settingsMessage.message_id
  currentChat.save()

# * Toggling values in the DB and updating lastMessagaID value
allCallbackDatas = [setting[1] for setting in settingsStrings]
@bot.callback_query_handler(func=lambda call: call.data in allCallbackDatas)
def callbackSettings(call):
  chatID = call.message.chat.id
  currentChat = None

  if call.data == settingsStrings[0][1]:
    currentChat = Chats.getChat(chatID)
    Settings.toggleSetting(currentChat, settingsStrings[0][2])

  if call.data == settingsStrings[1][1]:
    currentChat = Chats.getChat(chatID)
    Settings.toggleSetting(currentChat, settingsStrings[1][2])

  markup = settingsMarkup(chatID)
  try:
    bot.edit_message_text(
      Language(chatID).strs.stg, chatID,
      call.message.message_id,
      reply_markup=markup
    )
  except ApiException as e:
    print(e)