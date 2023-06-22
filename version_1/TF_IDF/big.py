# from nltk.corpus import wordnet
# import nltk
# nltk.download('wordnet')

# def is_english_word(word):
#     synsets = wordnet.synsets(word)
#     return len(synsets) > 0
# from nltk.stem import WordNetLemmatizer
# lemmatizer = WordNetLemmatizer()
# with open('version_1/TF_IDF/vocab.txt','r') as f:
#     documents = f.readlines()
#     for line in documents:
#         word = line.strip()
#         if word.isalpha() and len(word) > 2 and is_english_word(word):
#             print(lemmatizer.lemmatize(word))
# print(len(documents))

def check_vocab_in_file(vocab_file, target_file):
    with open(vocab_file, 'r') as vocab:
        vocab_words = set(word.strip() for word in vocab)

    with open(target_file, 'r') as target:
        target_words = set(word.strip() for word in target)

    common_words = vocab_words.intersection(target_words)

    for word in common_words:
        print(word)

# Example usage
vocab_file = 'TF_IDF/vocab.txt'
target_file = 'output5.txt'
check_vocab_in_file(vocab_file, target_file)
