from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import time
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
# Initialize the NLTK lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Define the custom delimiters for tokenization
custom_delimiters = r'(\(|\)|\[|\]|{|}|,)'

# Load TF-IDF matrix from file
with open('tfidf_matrix.pkl', 'rb') as file:
    tfidf_matrix = pickle.load(file)

# Load the vectorizer used to transform documents into TF-IDF matrix
with open('vectorizer.pkl', 'rb') as file:
    vectorizer = pickle.load(file)

start_time = time.time()

# Query and rank documents
line = "linked list"
line = line.strip()

        # Tokenize the line using custom delimiters and punctuation marks
tokens = nltk.word_tokenize(line.lower())

# Remove punctuation tokens
tokens = [token for token in tokens if token.isalnum()]

# Remove stopwords
tokens = [token for token in tokens if token not in stop_words]

# Lemmatize the words
lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]

query_vector = vectorizer.transform([(' '.join(lemmatized_tokens) + '\n')])  # Use transform instead of fit_transform

# Measure the execution time


similarity_scores = cosine_similarity(query_vector, tfidf_matrix)
sorted_indices = similarity_scores.argsort()[0][::-1]

# Calculate the execution time
execution_time = time.time() - start_time

# Load preprocessed documents
output_file_path = 'version_1/TF_IDF/qdata.txt'
with open(output_file_path, 'r') as f:
    preprocessed_documents = f.readlines()

# Print ranked documents with similarity scores
for index in sorted_indices:
    print(f"Document: {preprocessed_documents[index]}, Similarity Score: {similarity_scores[0][index]}")


# Print the execution time
print(f"Execution Time: {execution_time} seconds")




# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import TfidfVectorizer
# import pickle

# # Load TF-IDF matrix from file
# with open('tfidf_matrix.pkl', 'rb') as file:
#     tfidf_matrix = pickle.load(file)

# # Query and rank documents
# preprocessed_query = "linked list"
# vectorizer = TfidfVectorizer()  # Reinitialize the vectorizer
# query_vector = vectorizer.fit_transform([preprocessed_query])
# similarity_scores = cosine_similarity(query_vector, tfidf_matrix)
# sorted_indices = similarity_scores.argsort()[0][::-1]

# # Load preprocessed documents
# output_file_path = 'version_1/TF_IDF/documents.txt'
# with open(output_file_path, 'r') as f:
#     preprocessed_documents = f.readlines()

# # Print ranked documents
# for index in sorted_indices:
#     print(f"Document: {preprocessed_documents[index]}, Similarity Score: {similarity_scores[0][index]}")
