import math
import nltk
import time

from nltk.tokenize import regexp_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
lemmatizer = WordNetLemmatizer()
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import time
import nltk
from correct import correction

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from num2words import num2words
nltk.download('stopwords')
nltk.download('wordnet') 
nltk.download('punkt')
from nltk.corpus import stopwords

from num2words import num2words
stop_words = set(stopwords.words('english'))
from flask import Flask, jsonify, url_for, redirect, render_template, request, session
import math


with open('vectorizer.pkl', 'rb') as file:
    vectorizer = pickle.load(file)

 
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
    
            
with open('tfidf_matrix.pkl', 'rb') as file:
    tfidf_matrix = pickle.load(file) 

with open('version_1/Question_scrapper/Qdata/Qindex.txt', 'r') as f:
    qlinks = f.readlines()
with open('version_1/TF_IDF/qdata.txt', 'r') as f:
    qdata = f.readlines()
with open('version_1/Question_scrapper/Qdata/index.txt', 'r') as f:
    pname= f.readlines()
with open('version_1/TF_IDF/platform_name.txt', 'r') as f:
    platform = f.readlines() 

def calc_docs_sorted_order(query):

    query_vector = vectorizer.transform([query]) 
    similarity_scores = cosine_similarity(query_vector, tfidf_matrix)
    sorted_indices = similarity_scores.argsort()[0][::-1]
    ans = []
    for index in sorted_indices:
        ans.append({'Qlink': qlinks[index], 'score': similarity_scores[0][index], 'Qdata': qdata[index], 'pname': pname[int(index)], 'platform': platform[index]})
    
    return ans 
     

        

# query_string = input("Enter your query: ")
# query_string = "Given an array of positive integers nums, return the maximum possible sum of an ascending subarray in nums.A subarray is defined as a contiguous sequence of numbers in an array."
# query_string = remove_stop_words(query_string)
# start_time = time.time()

# # print(query_string)
# query_terms = [term.lower() for term in query_string.strip().split()]
# # # print(query_terms)

# p = calc_docs_sorted_order(preprocess(query_string))[:10:]

# print(p)
# execution_time =  time.time() - start_time
# print("Execution time:", execution_time, "seconds")


# for term in query_terms:
#     print(term, get_idf_value(term))
############################################################################################################


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/<query>")
def return_links(query):
    start_time = time.time()  # Start measuring time
    queryp=preprocess(query)
    results = calc_docs_sorted_order(queryp)[:20:]
    
    end_time = time.time()  # Stop measuring time
    execution_time = end_time - start_time
    return jsonify(results, execution_time)

@app.route("/", methods=['GET', 'POST'])
def home():
    search_term = session.pop('search_term', '') if 'search_term' in session else ''
    results = session.pop('results', []) if 'results' in session else []
    execution_time = session.pop('execution_time', 0) if 'execution_time' in session else 0
    query = ''
    if request.method == 'POST':
        query = request.form.get('search', '')
        # q_terms = [term.lower() for term in query.strip().split()]
        # results =  calc_docs_sorted_order(q_terms)[:10:]
        queryp=preprocess(query)
        results = calc_docs_sorted_order(queryp)[:20:]
        session['search_term'] = query
        session['results'] = results
        session['execution_time'] = execution_time
        return redirect(url_for('home'))
    # return render_template('index.html', search_term=search_term, results=paginated_results, execution_time=execution_time, total_pages=total_pages, current_page=page)
    return render_template('index.html', search_term=search_term, results=results, execution_time=execution_time)

if __name__ == '__main__':
    app.run(debug=True)
