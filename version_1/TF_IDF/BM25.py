

import time
from rank_bm25 import BM25Okapi
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import pickle



lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))




def load_bm25_model(filepath):
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model
bm25 = load_bm25_model('version_1/TF_IDF/bm25_model.pkl')
# Measure the execution time

start_time = time.time()
# Preprocess the query
preprocessed_query = "Given an unsorted array A of size N that contains only positive integers"


query_tokens = nltk.word_tokenize(preprocessed_query.lower())
query_tokens = [token for token in query_tokens if token.isalnum() and token not in stop_words]
query_tokens = [lemmatizer.lemmatize(token) for token in query_tokens]
preprocessed_query = ' '.join(query_tokens)

# Calculate BM25 scores for the query
query_scores = bm25.get_scores(preprocessed_query.split())

# Calculate the execution time
execution_time = time.time() - start_time
output_file_path = 'version_1/TF_IDF/qdata.txt'
# Load the ranked documents
with open(output_file_path, 'r') as f:
    ranked_documents = f.readlines()


# Print ranked documents with scores and execution time
for index, score in sorted(enumerate(query_scores), key=lambda x: x[1], reverse=True):
    print(f"Document: {ranked_documents[index]}, BM25 Score: {score}")
    
    

print(f"Execution time: {execution_time}")

# query_string = input("Enter your query: ")
# start_time = time.time()

# p = calc_docs_sorted_order(preprocess(query_string))[:10:]
# for i in p:
#     for j in i:
#         print(j, ":", i[j])
        
#     print("next result")
# execution_time =  time.time() - start_time
# print("Execution time:", execution_time, "seconds")
