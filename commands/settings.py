# ? Imports
from json import dumps

from config import (additionalButtonCallbacks, allSettingsCallbacks,
                    allSettingsEditingCallbacks, bot, commands)
from data_base import Chats, Settings, checkChat
from help_funcs import settingForUser, settingsMarkup
from language import Language
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# # ? Functions
# def setSetting(settingName, value, response):
#   """Will set setting to a passed value"""

#   Settings.setSetting()
#   return response


# * Command
@bot.message_handler(commands=[commands.stg])
def sendSettings(message):
  markup = settingsMarkup(message.chat.id)

  chatID = message.chat.id
  currentChat = Chats.getChat(message.chat.id)
  lastMessage = currentChat.settings.lastMessageId

  # * Deleting previous "settings" message
  try:
    if lastMessage[0]:
      bot.delete_message(chatID, lastMessage[0])
  except Exception:
    pass

  # * Sending new one
  settingsMessage = bot.send_message(
    chatID,
    message.replies.stg.msgTitle,
    reply_markup=markup
  )

  # * Setting new messageID when the message was send to be able to delete this one,
  # * when new settings will be sent

  currentChat.settings.lastMessageId = [
    settingsMessage.message_id,
    message.from_user.id
  ]
  currentChat.save()

# * Toggling values in the DB and updating lastMessagaID value
@bot.callback_query_handler(func=lambda call: call.data in allSettingsCallbacks)
def callbackSettings(call):
  chatId = call.message.chat.id
  currentChat = Chats.getChat(chatId)
  settingsStrings = call.replies.stg.strings

  # * Toggling setting, if a simple callback
  for i, callback in enumerate(allSettingsCallbacks):
    if call.data == callback:
      Settings.toggleSetting(currentChat, settingsStrings[i][0][3])

  # * Upating the message
  markup = settingsMarkup(chatId)
  try:
    bot.edit_message_text(
      Language(chatId).strs.stg.msgTitle, chatId,
      call.message.message_id,
      reply_markup=markup
    )

    bot.answer_callback_query(call.id, Language(chatId).strs.stg.success)
  except ApiException as e:
    print(e)

# * Callbacks for additional buttons in settings message
@bot.callback_query_handler(func=lambda call: call.data in additionalButtonCallbacks)
def callbackAdditionalButtons(call):
  chatId = call.message.chat.id
  currentChat = Chats.getChat(chatId)
  settingsStrings = call.replies.stg.strings

  # ? All buttons
  # * Edit values buttons
  if call.data == 'stgEditValues':
    botReplies = call.replies.stg
    userDmId = currentChat.settings.lastMessageId[1]

    # * Sending a message with a tag to move to bot's chat
    bot.send_message(chatId, botReplies.moveToChat.format(
      bot.get_me().username
    ))

    # * Creating a markup with all settings names, whose value can be edited
    markup = InlineKeyboardMarkup()
    for setting in settingsStrings:
      for button in setting:
        if button[2]:
          # * Converts in a strange way to get 'Test String' from 'testString'
          text = settingForUser(button[3])
          tempButton = InlineKeyboardButton(
            # ~ Converts 'testMessage' to 'Test Message'
            text,
            callback_data=dumps([
              button[1].replace('stg', 'edit'),
              button[3]
            ])
          )
          markup.row(tempButton)

    checkChat(userDmId)
    dmChat = Chats.getChat(userDmId)
    dmChat.settings.editMessageInfo['originalChatId'] = call.message.chat.id
    dmChat.save()

    bot.send_message(userDmId, botReplies.editorMessage, reply_markup=markup)

  # * More info button
  if call.data == 'stgMoreInfo':
    allSettingsNames = []
    for setting in settingsStrings:
      for button in setting:
        allSettingsNames.append(settingForUser(button[3]))

    text = '\n\n'.join(call.replies.stg.additionalInfo).format(*allSettingsNames)
    bot.send_message(chatId, text, parse_mode='html')


# * Callbacking buttons for editing saves info will be needed to change settings
@bot.callback_query_handler(func=lambda call: call.data in allSettingsEditingCallbacks)
def callbackSettingsEditors(call):
  currentChat = Chats.getChat(call.message.chat.id)
  # * Sending a helping message and updating the DB
  newMessage = bot.send_message(call.message.chat.id, call.replies.stg.sendNewValue)
  
  addingInfoTo = currentChat.settings.editMessageInfo
  addingInfoTo['requestMessageId'] = newMessage.message_id
  addingInfoTo['requestChatId'] = newMessage.chat.id
  addingInfoTo['commandName'] = call.additionalInfo
  addingInfoTo['callbackId'] = call.id

  currentChat.save()

# * InlineQueries to set settings values
# @bot.inline_handler(lambda query: True)
# def query_text(inline_query):
#   print(inline_query)
#   # * Saves string for the article for this user language
#   allStrings = Language.byLanguageCode(
#     inline_query.from_user.language_code
#   ).stg
#   settingStrings = allStrings.settingsEditor

#   try:
#     # description='Sets number of responses to start deleting previous bot responses. Helps to keep chat clean. You can set values between 5 and 100.',
#     allArticles = []
#     for i, _ in enumerate(settingStrings):
#       arguments = inline_query.query.split()
#       response = allStrings.noArgsPassed

#       # * Changes a response to correct one for this paricural situations
#       # * if number of arguments is corrent for this command
  
#       if len(arguments) >= len(settingStrings[i][0].split()) + 1:
#         response = setSetting(settingStrings[i], arguments[1], allStrings.valueSet)

#       print(response)
#       acceptEditingKeyboard = InlineKeyboardMarkup()
#       acceptEditingKeyboard.row(
#         InlineKeyboardButton('Apply setting', callback_data=dumps([
#           'setSetting', arguments[:1]
#         ])),
#         InlineKeyboardButton('Cancel', callback_data='deleteMessage')
#       )

#       allArticles.append(InlineQueryResultArticle(
#         inline_query.id,
#         title=settingStrings[i][0],
#         description=settingStrings[i][1],
#         input_message_content=InputTextMessageContent(response),
#         reply_markup=acceptEditingKeyboard
#       ))

#     bot.answer_inline_query(inline_query.id, allArticles)
#   except IndexError:
#     print(e)
