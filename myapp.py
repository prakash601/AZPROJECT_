from flask import Flask, jsonify, url_for, redirect, render_template, request, session
import math
import re
import time
from rank_bm25 import BM25Okapi
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import pickle
from correct import correction
from num2words import num2words
nltk.download('stopwords')
nltk.download('wordnet') 
nltk.download('punkt')

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
query = "linked list"


# query_tokens = nltk.word_tokenize(preprocessed_query.lower())
# query_tokens = [token for token in query_tokens if token.isalnum() and token not in stop_words]
# query_tokens = [lemmatizer.lemmatize(token) for token in query_tokens]
# preprocessed_query = ' '.join(query_tokens)
def preprocess(text):
    line = text.strip()
    tokens = nltk.word_tokenize(line.lower())
    tokens = [t for t in tokens if t.isalnum()]
    tokens = [t for t in tokens if t not in stop_words]
    # tokens = expand_query(tokens)
    corrected_tokens = []
    for token in tokens:
        correction_res = correction(token)
        if token.isdigit():
            corrected_tokens.append(num2words(int(token)))
        else:
            corrected_tokens.append(correction_res)
    # print(f"Misspelled word: {token}, Correction: {correction_res}")
    lem_tokens = [lemmatizer.lemmatize(token) for token in corrected_tokens]
    query = ' '.join(lem_tokens)
    # print(query)
    # query_vector = vectorizer.transform([query]) 
    return query

# Calculate BM25 scores for the query
# query_scores = bm25.get_scores(preprocess(query).split())

# Calculate the execution time
execution_time = time.time() - start_time
output_file_path = 'version_1/TF_IDF/qdata.txt'
# Load the ranked documents
# with open(output_file_path, 'r') as f:
#     ranked_documents = f.readlines()

with open('version_1/Question_scrapper/Qdata/Qindex.txt', 'r') as f:
    qlinks = f.readlines()
with open('version_1/TF_IDF/qdata.txt', 'r') as f:
    qdata = f.readlines()
with open('version_1/Question_scrapper/Qdata/index.txt', 'r') as f:
    pname= f.readlines()
with open('version_1/TF_IDF/platform_name.txt', 'r') as f:
    platform = f.readlines() 

def calc_docs_sorted_order(query):
    query_scores = bm25.get_scores(preprocess(query).split())
    ans = []
    # Print ranked documents with scores and execution time
    i=0
    for index, score in sorted(enumerate(query_scores), key=lambda x: x[1], reverse=True):
        ans.append({'Qlink': qlinks[index], 'score': score, 'Qdata': qdata[index], 'pname': pname[int(index)], 'platform': platform[index]})
        if i == 50:
            break
        # print(f"Document: {qdata[index]}, BM25 Score: {score}")
    return ans

# query_string = input("Enter your query: ")
# p = calc_docs_sorted_order(preprocess(query_string))[:10:]
# # print(p)
# for i in p:
#     for j in i:
#         print(j, ":", i[j])
        
#     print("next result")
# execution_time =  time.time() - start_time
# print("Execution time:", execution_time, "seconds")


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/<query>')
def return_links(query):
    results = calc_docs_sorted_order(preprocess(query))[:30:]
    return jsonify(results=results)

@app.route('/', methods=['GET', 'POST'])
def home():
    query= ''
    queryp = ''
    results = []
    execution_time = 0
    if request.method == 'POST':
        query = request.form['search']
        # print(f"Received query: {query}")  # Debug print statement
        start_time = time.time()
        queryp = preprocess(query)
        results = calc_docs_sorted_order(queryp)[:30:]
        execution_time = time.time() - start_time
        # print(f"Results: {results}")  # Debug print statement
        # return redirect(url_for('home'))
    
    return render_template('index.html',results=results, query=query, queryp=queryp, execution_time=execution_time)

if __name__ == '__main__':
    app.run(debug=True)