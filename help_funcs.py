import config

def wordContains(word, checkArray):
  for char in word:
    if char in checkArray:
      return True
  return False

def splitSentence (toSplit):
  result = []
  fullArray = [*config.letters, *config.numbers]

  for char in toSplit:
    if char in fullArray:
      result.append(char)
  resultArray = (''.join(result)).split(' ')
  result = []

  for word in resultArray:
    if wordContains(word, config.letters):
      result.append(word)

  return result

def allArrayToLowercase(array):
  result = []
  for item in array:
    result.append(str (item).lower ())
  return result
