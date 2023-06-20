import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from rank_bm25 import BM25Okapi
import pickle
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

output_file_path = 'version_1/TF_IDF/documents.txt'
with open(output_file_path, 'r') as f:
    preprocessed_documents = f.readlines()

def preprocess_text(text):
    tokens = nltk.word_tokenize(text.lower())
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text

documents = [preprocess_text(doc) for doc in preprocessed_documents]

def create_bm25_model(documents):
    tokenized_documents = [nltk.word_tokenize(doc.lower()) for doc in documents]
    tokenized_documents = [[token for token in doc if token.isalnum()] for doc in tokenized_documents]
    tokenized_documents = [[lemmatizer.lemmatize(token) for token in doc] for doc in tokenized_documents]

    bm25 = BM25Okapi(tokenized_documents)
    return bm25

def save_bm25_model(model, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)

bm25_model = create_bm25_model(documents)
model_file_path = 'version_1/TF_IDF/bm25_model.pkl'

save_bm25_model(bm25_model, model_file_path)

# def load_bm25_model(filepath):
#     with open(filepath, 'rb') as f:
#         model = pickle.load(f)
#     return model





# import nltk
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer

# def preprocess_text(text):
#     lemmatizer = WordNetLemmatizer()
#     stop_words = set(stopwords.words('english'))

#     tokens = nltk.word_tokenize(text.lower())
#     tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
#     tokens = [lemmatizer.lemmatize(token) for token in tokens]
#     preprocessed_text = ' '.join(tokens)

#     return preprocessed_text