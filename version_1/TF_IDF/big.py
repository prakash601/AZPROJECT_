from nltk.corpus import wordnet
import nltk
nltk.download('wordnet')

def is_english_word(word):
    synsets = wordnet.synsets(word)
    return len(synsets) > 0
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
with open('version_1/TF_IDF/vocab.txt','r') as f:
    documents = f.readlines()
    for line in documents:
        word = line.strip()
        if word.isalpha() and len(word) > 2 and is_english_word(word):
            print(lemmatizer.lemmatize(word))
# print(len(documents))
