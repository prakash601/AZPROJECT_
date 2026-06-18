from flask import Flask, jsonify, url_for, redirect, render_template, request, session
import math
import re
import time
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from correct import correction
from num2words import num2words
from search import search as pg_search, autocomplete

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Legacy BM25 search has been removed as it relied on the now-deleted data/ directory.

def correct_query(text):
    line = text.strip()
    tokens = nltk.word_tokenize(line)
    corrected_tokens = []
    for token in tokens:
        correction_res = correction(token)
        if token.isdigit():
            corrected_tokens.append(num2words(int(token)))
        else:
            corrected_tokens.append(correction_res)
    query = ' '.join(corrected_tokens)
    return query

# ============================================================
# Flask App
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['TEMPLATES_AUTO_RELOAD'] = True


# --- New PostgreSQL-powered routes ---

@app.route('/api/search/<query>')
def api_search(query):
    """API endpoint: PostgreSQL hybrid search (semantic + FTS + trigram)."""
    results = pg_search(query, limit=30)
    return jsonify(results=results)


@app.route('/api/autocomplete/<prefix>')
def api_autocomplete(prefix):
    """API endpoint: fast autocomplete via trigram + prefix matching."""
    results = autocomplete(prefix, limit=10)
    return jsonify(results=results)


@app.route('/', methods=['GET', 'POST'])
def home():
    """Main search page — uses PostgreSQL hybrid search."""
    query = ''
    queryp = ''
    results = []
    execution_time = 0
    if request.method == 'POST':
        query = request.form['search']
        start_time = time.time()
        queryp = correct_query(query)
        results = pg_search(query, limit=30)
        execution_time = time.time() - start_time

    return render_template(
        'index.html',
        results=results,
        query=query,
        queryp=queryp,
        execution_time=execution_time
    )





if __name__ == '__main__':
    app.run(debug=True)