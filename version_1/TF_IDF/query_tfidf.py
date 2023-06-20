import math
import nltk
import time
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
lemmatizer = WordNetLemmatizer()
# nltk.download('stopwords')
# nltk.download('wordnet') 
# nltk.download('wordnet')



from flask import Flask, jsonify
import math
import re

from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

astop_words = set(stopwords.words('english'))
custom_stop_words = ['<','<=', '=', '<', '>=','r', ',',']','.','[','(',')','+','-','return','given','--','//','/','*','**','**=','*=','+=','-=','==','!=','!=','+=','-=','*=','/=','%=', '||', '!', '&&', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '>>=', '<<=','!', '@', '#', '$', '%', '&', '*', '(', ')', '-', '+', '=', '[', ']', '{', '}', '|',
    '\\', '/', '~', '^', '>', '<', '.', ',', ':', ';', '"', "'", '_', '?', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F', 'G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U', 'V','W','X','Y','Z','`','``','````','``````','````````','``````````','```````````','````````````','`````````````','``````````````','```````````````','````````````````','`````````````````','``````````````````','```````````````````', '``',
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'in', 'on', 'at', 'by', 'to', 'for',
    'with', 'and', 'or', 'not', 'but', 'from', 'into', 'about', 'after', 'before', 'over',
    'under', 'between', 'among', 'through', 'during', 'since', 'until', 'unless', 'while',
    'throughout', 'above', 'below', 'behind', 'beside', 'beneath', 'within', 'without',
    'Hello', ',', 'how', 'are', 'you', '?', '(', "I'm", 'doing', 'well', ')', '[', 'And', 'you', ']', '{', 'Nice', 'to', 'meet', 'you', '}', '&', '(', '...', ')', ',', '[', '..', ':', ']', '....', '+-----------------+----------+|', '|+-----------------+----------+|', '|+-----------------+----------+', '"||**||**|*"', '", "', '=#', ',', '#,', '#,#"', ',', ',', ':"../"', ').', '"./"', '/"'
 ]


stop_words = astop_words.union(custom_stop_words)

def remove_stop_words(text):
    
    words = regexp_tokenize(text, pattern=r"\w+|[^\w\s]|\(|\)|\[|\]|{|}|,|\.|\+|-|:|\"|&|\*|/|=|#")
    # words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)


def preprocess(document_text):
    filtered_terms = remove_stop_words(document_text).strip().split()
    lemmatized_terms = [lemmatizer.lemmatize(term.lower()) for term in filtered_terms]
    return lemmatized_terms

def load_vocab(): 
    vocab = {}
    with open('version_1/TF_IDF/vocab.txt','r') as f:
        vocab_terms = f.readlines()
    with open('version_1/TF_IDF/idf-values.txt','r') as f:
        idf_values = f.readlines()
    
    for (term, idf_value) in zip(vocab_terms, idf_values):
        vocab[term.strip()] = int(idf_value.strip()) 
    # print('size of vocab', len(vocab))
    return vocab 


def load_documents():
    documents = []
    with open('version_1/TF_IDF/documents_tfidf.txt','r') as f:
        documents = f.readlines()
    documents = [doc.strip().split() for doc in documents]
    print('numner of documents', len(documents))
    print('sample document', documents[0])
    return documents

def load_inverted_index():
    inverted_index = {}
    with open('version_1/TF_IDF/inverted_index_tfidf.txt','r') as f:
        inverted_index_terms = f.readlines()
    
    for row_num in range(0,len(inverted_index_terms),2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num+1].strip().split()
        inverted_index[term] = documents
    # print('size of inverted index', len(inverted_index))
    return inverted_index
 
 
 
 
def load_links_of_qs():
    with open("version_1/Question_scrapper/Qdata/Qindex.txt", "r") as f:
        links = f.readlines()
    return links


Qlink = load_links_of_qs() 

# get the document text from document.txt 
def load_doc_text():
    with open("version_1/TF_IDF/documents.txt", "r") as f:
        docs = f.readlines()
    return docs

Doctext = load_doc_text()

vocab_idf_vales = load_vocab()
documents = load_documents()
inverted_index = load_inverted_index()
# print(inverted_index['the'])  
 


def get_tf_dictionary(term):
    tf_vlaues = {}
    if term in inverted_index:
        for doc_id in inverted_index[term]:
            if doc_id not in tf_vlaues:
                tf_vlaues[doc_id] = 1
            else:
                tf_vlaues[doc_id] += 1
    for document in tf_vlaues:
        # tf_vlaues[document] = math.log(tf_vlaues[document] + 1)
        # tf_vlaues[document] = tf_vlaues[document] / len(documents[int (document)])
        max_tf = max(tf_vlaues.values())
        avg_tf = sum(tf_vlaues.values()) / len(tf_vlaues)
        for document in tf_vlaues:
            tf_vlaues[document] = tf_vlaues[document] / max_tf / avg_tf

    return tf_vlaues

# def get_idf_value(term):  
#     return math.log(len(documents) / vocab_idf_vales[term])
    
def get_idf_value(term):
    df = len(inverted_index.get(term, []))
    smoothing_term = 1  # Adjust the value of the smoothing term as per your preference
    idf = math.log((len(documents) + smoothing_term) / (df + smoothing_term))
    return idf

def calc_docs_sorted_order(q_terms):
    potential_docs = {}
    ans = []
    
    for term in q_terms:
        if (term not in vocab_idf_vales):
            continue

        tf_vals_by_docs = get_tf_dictionary(term)
        idf_value = get_idf_value(term)

        for doc in tf_vals_by_docs:
            if doc not in potential_docs:
                potential_docs[doc] = tf_vals_by_docs[doc] * idf_value
            else:
                potential_docs[doc] += tf_vals_by_docs[doc] * idf_value

    # Divide the scores of each doc by the number of query terms
    for doc in potential_docs:
        potential_docs[doc] /= len(q_terms)

    # Sort in descending order according to the calculated values
    sorted_docs = dict(sorted(potential_docs.items(), key=lambda item: item[1], reverse=True))

    if len(sorted_docs) == 0:
        print("No matching question found. Please search with more relevant terms.")
        return ans
    
    for doc_index in sorted_docs:
        ans.append({
            "Question Link": Qlink[int(doc_index)][:-1],
            "text": Doctext[int(doc_index)]
        })
        break
        # print('score: ', potential_docs[doc_index], 'Document: ',documents[int(doc_index)])

    return ans
     
     

    # i=0
    # for i, document_index in enumerate(potential_documents):
    #     if i == 10:
    #         break
    #     print('Score:', potential_documents[document_index], 'Document:', documents[int(document_index)])
        
        # for document_index in potential_documents:
        #     print('score: ', potential_documents[document_index], 'Document: ',documents[int(document_index)])

        
    
    # i=0
    # for i, document_index in enumerate(potential_documents):
    #     if i == 10:
    #         break
    #     print('Score:', potential_documents[document_index], 'Document:', documents[int(document_index)])
        
        # for document_index in potential_documents:
        #     print('score: ', potential_documents[document_index], 'Document: ',documents[int(document_index)])

        

# query_string = input("Enter your query: ")
query_string = "linked list"
start_time = time.time()
text = remove_stop_words(query_string)
# corrected_text = correct_spellings(text)
print(text)
query_terms = preprocess(text)

print(query_terms)
p=calc_docs_sorted_order(query_terms)
# p=calc_docs_sorted_order(preprocess(remove_stop_words(query_string)))
print(p[:20:])

end_time = time.time()
execution_time = end_time - start_time
print("Execution time:", execution_time, "seconds")

# # for term in query_terms:
#     print(term, get_idf_value(term))

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key'

# class SearchForm(FlaskForm):
#     search = StringField('Enter your search term')
#     submit = SubmitField('Search')


# @app.route("/<query>")
# def return_links(query):
#     query_terms = [term.lower() for term in query.strip().split()]
#     return jsonify(calculate_sorted_order_of_documents(query_terms)[:20:])


# @app.route("/", methods=['GET', 'POST'])
# def home():
#     form = SearchForm()
#     results = []
#     if form.validate_on_submit():
#         query = form.search.data
#         query_terms = [term.lower() for term in query.strip().split()]
#         results = calculate_sorted_order_of_documents(query_terms)[:20:]
#     return render_template('index.html', form=form, results=results)