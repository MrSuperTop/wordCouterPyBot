# ? Imports
# * MongoDB
from mongoengine import connect
from mongoengine.errors import DoesNotExist
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import IntField, StringField, EmbeddedDocumentField, EmbeddedDocumentListField

# * Connection to the local Mongo DB
connect('word-counter-bot')

# ? Documents
class Word(EmbeddedDocument):
  """Message Document which will be used in a server document. Saves basic info about each individual word"""

  text = StringField(required=True)
  sentTimes = IntField()

class Chats(Document):
  """Chat document saves all words + language settings of a chat. Most used word object is save here too"""

  language = StringField()
  ID = IntField()
  words = EmbeddedDocumentListField(Word)

  sentWords = IntField()
  sentMessages = IntField()

  topWord = EmbeddedDocumentField(Word)


# word = Word(
#   text = 'Hello',
#   sentTimes = 1
# )

# firstChat = Chats(
#   language = "Eng",
#   ID = 123,
#   words = [word],
#   topWord = word
# ).save()

# # chats = Chat.objects()

# # for chat in chats:
# #   print(chat.words[0].content)

# chats = Chat.objects(ID=123)
# for chat in chats:
#   print(chat.words[0].content)
