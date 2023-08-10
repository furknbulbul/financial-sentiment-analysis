import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

lemmatizer = WordNetLemmatizer()
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
stopwordsList = stopwords.words('english')


def textCleaning(text):

  # Step 1: Make them all lower case
  text = text.lower()

  # Step 2: Remove punctions
  # translator = str.maketrans("", "", string.punctuation)
  # text = text.translate(translator)
  # dozens injured as apple-sized hailstones hit colorado concertgoers
  # dozens injured as applesized hailstones hit colorado concertgoers

  punctions = ".,:;?!/\"\'`*(){}[]%+^#&‘’|–$€₺"

  for punc in punctions:
    text = text.replace(punc, "")

  text = text.replace("-", " ")
  text = text.replace("_", " ")
  text = text.replace("  ", " ")

  # Step 3: Remove numbers
  text = re.sub(r'\d+', '', text)

  # Step 4: Remove URLs
  text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)

  # Step 5: Tokenization
  wordTokens = nltk.word_tokenize(text)

  # Step 6: Remove Stop Words
  filteredText = [word for word in wordTokens if word not in stopwordsList]

  # Step 7: Lemmatization (running, runner, ran, runs) -> (run, runner, run, run)
  lemmatizedWords = [lemmatizer.lemmatize(word) for word in filteredText]

  # Step 8: Combine the seperated words
  finalText = ' '.join(lemmatizedWords)

  return finalText

# datanew['cleaned_text'] = datanew['webtitle'].apply(textCleaning)

cleanedText = textCleaning("This is a demo text!!!")
cleanedText