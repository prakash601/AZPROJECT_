from flask import Flask, jsonify, url_for, redirect, render_template, request, session
import math
import re
import time
from rank_bm25 import BM25Okapi
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import pickle

nltk.download('stopwords')
nltk.download('wordnet') 
nltk.download('wordnet')


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
preprocessed_query = "linked list"


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
    break

print(f"Execution time: {execution_time}")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/<query>')
def return_links(query):
    # Measure the execution time
    start_time = time.time()
    # Preprocess the query
    preprocessed_query = query


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
    with open('version_1/Qdata/Qindex.txt', 'r') as f:
        qlinks = f.readlines()
    with open('version_1/Qdata/Qdata.txt', 'r') as f:
        qdata = f.readlines()
    with open('version_1/Qdata/index.txt', 'r') as f:
        pname= f.readlines()
    with open('version_1/TF_IDF/platform_name.txt', 'r') as f:
        platform = f.readlines()
        
    results = {}
    # Print ranked documents with scores and execution time
    for index, score in sorted(enumerate(query_scores), key=lambda x: x[1], reverse=True):
        ans.append({'Qlink': qlinks[int(index)], 'score': score, 'Qdata': qdata[int(index)], 'pname': pname[int(index)], 'platform': platform[int(index)]})
        # print(f"Document: {ranked_documents[index]}, BM25 Score: {score}")
    execution_time = time.time() - start_time
    # print(f"Execution time: {execution_time}")
    return jsonify(results , execution_time)

@app.route('/', methods=['GET', 'POST'])
def home():
    search_term = session.pop('search_term', '') if 'search_term' in session else ''
    results = session.pop('results', []) if 'results' in session else []
    execution_time = session.pop('execution_time', 0) if 'execution_time' in session else 0
    if request.method == 'POST':
        search_term = request.form['search']
        session['search_term'] = search_term
        return redirect(url_for('home'))
    
    return render_template('index.html', search_term=search_term, results=results, execution_time=execution_time)

if __name__ == '__main__':
    app.run(debug=True)