from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from num2words import num2words
import re
from correct import correction

# Load TF-IDF matrix from file
with open('tfidf_matrix.pkl', 'rb') as file:
    tfidf_matrix = pickle.load(file)

# Load the vectorizer used to transform documents into TF-IDF matrix
with open('vectorizer.pkl', 'rb') as file:
    vectorizer = pickle.load(file)

# Initialize NLTK lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Measure the execution time
start_time = time.time()

# Query and rank documents
line = "linkad liast is a thas 1"
line = line.strip()

# Tokenize the line using custom delimiters and punctuation marks
tokens = nltk.word_tokenize(line.lower())

# Remove punctuation tokens
tokens = [token for token in tokens if token.isalnum()]

# Remove stopwords
tokens = [token for token in tokens if token not in stop_words]

corrected_tokens = []
for token in tokens:
    correction_res = correction(token)
    if token.isdigit():
        corrected_tokens.append(num2words(int(token)))
    else:
        corrected_tokens.append(correction_res)
    print(f"Misspelled word: {token}, Correction: {correction_res}")
    # if correction.isdigit():
    #     corrected_tokens.append(num2words(int(correction_res)))
    # else:
    #     corrected_tokens.append(correction_res)
    # print(f"Misspelled word: {token}, Correction: {correction_res}")

# Lemmatize the words
lemmatized_tokens = [lemmatizer.lemmatize(token) for token in corrected_tokens]

query_vector = vectorizer.transform([' '.join(lemmatized_tokens)])  # Use transform instead of fit_transform

similarity_scores = cosine_similarity(query_vector, tfidf_matrix)
sorted_indices = similarity_scores.argsort()[0][::-1]

# Calculate the execution time
execution_time = time.time() - start_time

# Load preprocessed documents
output_file_path = 'version_1/TF_IDF/documents.txt'
with open(output_file_path, 'r') as f:
    preprocessed_documents = f.readlines()

# Print ranked documents with similarity scores
for index in sorted_indices:
    print(f"Document: {preprocessed_documents[index]}, Similarity Score: {similarity_scores[0][index]}")
    break

# Print the execution time
print(f"Execution Time: {execution_time} seconds")
