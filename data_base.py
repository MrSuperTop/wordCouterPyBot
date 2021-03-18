# ? Imports



from typing import Union, Type

from bson.json_util import default

# * MongoDB
from mongoengine import connect
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.errors import DoesNotExist
from mongoengine.fields import (BooleanField, DictField, EmbeddedDocumentField,
                                EmbeddedDocumentListField, IntField, ListField,
                                StringField)

# * Telebot
from telebot.types import Message


# * Connection to the local Mongo DB
connect('word-counter-bot')

# ? Documents
class Settings(EmbeddedDocument):
  """Chat settings, unicue for each chat"""

  sendPrivate = BooleanField(default=False)
  removeAfter = DictField(default={
    'haveTo': True,
    'numberOfMessages': 5
  })

  lastMessageID = IntField(default=0)

  @staticmethod
  def toggleSetting(chat, settingKey: str) -> None:
    """
    Will toggle a value of a setting by a provied key as "settingKey" value weather
    it's a simle bool field, or a more comlicated dict field.
    """

    currentSetting = chat.settings[settingKey]
    if isinstance(currentSetting, bool):
      chat.settings[settingKey] = not currentSetting
    elif isinstance(currentSetting, dict):
      chat.settings[settingKey]['haveTo'] = not currentSetting['haveTo']

    chat.save()

class Word(EmbeddedDocument):
  """
  Message Document which will be used in a server document.
  Saves basic info about each individual word
  """

  text = StringField(required=True)
  sentTimes = IntField()

class Chats(Document):
  """Chat document saves all words + language settings of a chat. Most used word object is save here too"""

  language = StringField()
  ID = IntField()
  settings = EmbeddedDocumentField(Settings)

  words = EmbeddedDocumentListField(Word)
  responses = DictField(default={})

  sentWords = IntField()
  sentMessages = IntField()

  topWord = EmbeddedDocumentField(Word)

  @staticmethod
  def getChat(chatID):
    """Will return a chat object when ID is provided"""

    return Chats.objects(ID=chatID).get()

  @staticmethod
  def getSettings(chatID):
    """Will return a settings object to simplify querry the db"""

    settingsObjects = Chats.objects(ID=chatID).get().settings
    return settingsObjects

# ? Classes to work with the db
# * Responses manager class
class ResponsesManager:
  """
  Has methods to delete delete and add elements for responses object in the database.\n
  All the nessesary information is provided to the constructor.
  """

  intAndMessageTyping = Union[int, Type[Message]]

  def __init__(self, chat: Union[Type[Chats], Type[Message]]):
    """
    Will add a chat attribute from the value you passed to the constructor.
    "Chat" parameter can be a Chats object allready, or you can pass a Message
    object the method will query the database and get info it needs.
    """

    if isinstance(chat, Message):
      self.chat = Chats.objects(ID=chat.chat.id)
      return None

    self.chat = chat

  def __getMessageID(func):
    """
    Will get mesage_id from gettingFrom attribute weather
    it's a Message object or message_id already
    """

    def decorator(self, gettingFrom: Union[int, Type[Message]], *args, **kwargs):
      if isinstance(gettingFrom, Message):
        gettingFrom =  gettingFrom.message_id

      func(self, gettingFrom, *args, **kwargs)

    return decorator

  @__getMessageID
  def deleteResponse(self, messageID: intAndMessageTyping):
    del self.chat.responses[str(messageID)]
    self.chat.save()

  @__getMessageID
  def addResponse(self, messageID: intAndMessageTyping):
    self.chat.responses[str(messageID)] = {
      'connectedIDs': {}
    }

    self.chat.save()

  @__getMessageID
  def addIDs(self, messageID, ids: Union[list, int]=None, chatIdSentTo: int=None):
    if not isinstance(ids, list):
      ids = [ids]

    if chatIdSentTo == None:
      chatIdSentTo = self.chat.ID

    ids = [id.message_id for id in ids]

    # * Response dictionary message "value", which coresponds to this particular "main" message id
    responseMessage = self.chat.responses[str(messageID)]
    # * Saves "connectedIDs" dictionary to the variable, gets from the DB
    connectedIds = responseMessage['connectedIDs']

    allChatIds = [int(id[0]) for id in connectedIds.items()]

    for id in ids:
      if chatIdSentTo in allChatIds:
        # * Adding Id to an array with chatId, which matching one we want to add
        connectedIds[str(chatIdSentTo)].append(id)
      else:
        connectedIds[str(chatIdSentTo)] = [id]

    self.chat.save()

  @staticmethod
  def getIDs(chat, messageID):
    messageConnectedIds = [id[0] for id in chat.responses[str(messageID)]['connectedIDs']]
    return messageConnectedIds

# ? Functions to help working with the database
def checkChat(chatID):
  """Checks if the chat exists in the database,
  if doesn't fills it with basic placeholder info
  and saves it to the database"""

  try:
    Chats.objects(ID=chatID).get()
  except Chats.DoesNotExist:
    Chats(
      language = "eng",
      ID = chatID,
      settings = Settings(
        sendPrivate = False
      ),
      words = [],
      topWord = Word(
        text = '',
        sentTimes = 1
      ),
      sentWords = 0,
      sentMessages = 0
    ).save()

