# ? Import
from typing import Union, Type

from telebot.types import CallbackQuery, Message

from config import dotdict, replies, implamentedLanguages
from data_base import Chats, checkChat

# ? Classes
# * Language class, which will be used in main program
class Language:
  """
  Class, which will allow to accecs strings for a particular language,
  has to be updated in the middlewera every time is used, so it will
  provide up-to-date strings. It's made using getter and setter.
  """

  _language = 'eng'
  _strings = dotdict()

  @staticmethod
  def idFromObject(objectWithID):
    """Will extract"""
    chatID = 0

    if isinstance(objectWithID, int):
      return objectWithID
    if isinstance(objectWithID, Message):
      chatID = objectWithID.chat.id
    if isinstance(objectWithID, CallbackQuery):
      chatID = objectWithID.message.chat.id

    return chatID

  # * Init
  def __init__(self, objectWithID=None):
    if objectWithID:
      chatID = self.idFromObject(objectWithID)
      try:
        currentChat = Chats.getChat(chatID)

        self._language = currentChat.language
      except Chats.DoesNotExist:
        checkChat(chatID)
        self._language = 'eng'

      self._strings = replies[self._language]

  
  # ? Getters and setters, which will be used with this class
  @property
  def strs(self) -> dotdict:
    """
    Retruns a special class objects, which has all bot replies
    for this current chat and language it's using
    """

    return self._strings

  @property
  def lang(self) -> str:
    return self._language

  @lang.setter
  def lang(self, values) -> None:
    objectWithID, newLanguage = values
    currentChat = Chats()

    # * Checking if provided language exists in the database
    if newLanguage in implamentedLanguages:
      for _ in range(2):
        chatID = self.idFromObject(objectWithID)
        try:
          currentChat = Chats.getChat(chatID)
        except Chats.DoesNotExist:
          checkChat(chatID)

    currentChat.language = newLanguage
    currentChat.save()

    self._strings = replies[newLanguage]
    self._language = newLanguage

  @staticmethod
  def byLanguageCode(code: str) -> Union[Type[dotdict], None]:
    """
    Will return replies strings for a provided language code ('ru', 'eng', etc.).
    If the lanugale code is not found in the config will return strings for English.
    """

    result = replies.get(code, None)
    if result is None:
      result = replies.eng
    return result
