import time
from rank_bm25 import BM25Okapi
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import pickle

# Load and preprocess documents
output_file_path = 'version_1/TF_IDF/documents.txt'
with open(output_file_path, 'r') as f:
    preprocessed_documents = f.readlines()

# Preprocess the query
preprocessed_query = "linked list"
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
query_tokens = nltk.word_tokenize(preprocessed_query.lower())
query_tokens = [token for token in query_tokens if token.isalnum() and token not in stop_words]
query_tokens = [lemmatizer.lemmatize(token) for token in query_tokens]
preprocessed_query = ' '.join(query_tokens)

# Tokenize and preprocess the documents
tokenized_documents = [nltk.word_tokenize(doc.lower()) for doc in preprocessed_documents]
tokenized_documents = [[token for token in doc if token.isalnum() and token not in stop_words] for doc in tokenized_documents]
tokenized_documents = [[lemmatizer.lemmatize(token) for token in doc] for doc in tokenized_documents]

# Create the BM25 model
bm25 = BM25Okapi(tokenized_documents)

# Measure the execution time
start_time = time.time()

# Calculate BM25 scores for the query
query_scores = bm25.get_scores(preprocessed_query.split())

# Calculate the execution time
execution_time = time.time() - start_time

# Load the ranked documents
with open(output_file_path, 'r') as f:
    ranked_documents = f.readlines()


# Print ranked documents with scores and execution time
for index, score in sorted(enumerate(query_scores), key=lambda x: x[1], reverse=True):
    print(f"Document: {ranked_documents[index]}, BM25 Score: {score}")


