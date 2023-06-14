import math
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# nltk.download('stopwords')
# nltk.download('punkt')

astop_words = set(stopwords.words('english'))
custom_stop_words = ['<','<=', '=', '<', '>=','r', ',',']','.','[']
stop_words = astop_words.union(custom_stop_words)

def remove_stop_words(text):
    # words = word_tokenize(text)
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def load_vocab(): 
    vocab = {}
    with open('TF_IDF/vocab.txt','r') as f:
        vocab_terms = f.readlines()
    with open('TF_IDF/idf-values.txt','r') as f:
        idf_values = f.readlines()
    
    for (term, idf_value) in zip(vocab_terms, idf_values):
        vocab[term.strip()] = int(idf_value.strip()) 
    # print('size of vocab', len(vocab))
    return vocab 


def load_documents():
    documents = []
    with open('TF_IDF/documents.txt','r') as f:
        documents = f.readlines()
    documents = [doc.strip().split() for doc in documents]
    # print('numner of documents', len(documents))
    # print('sample document', documents[0])
    return documents

def load_inverted_index():
    inverted_index = {}
    with open('TF_IDF/inverted_index.txt','r') as f:
        inverted_index_terms = f.readlines()
    
    for row_num in range(0,len(inverted_index_terms),2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num+1].strip().split()
        inverted_index[term] = documents
    # print('size of inverted index', len(inverted_index))
    return inverted_index
 
 
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
        tf_vlaues[document] = tf_vlaues[document] / len(documents[int (document)])
    return tf_vlaues

def get_idf_value(term):  
    return math.log(len(documents) / vocab_idf_vales[term])
    


def calculate_sorted_order_of_documents(query_terms):
    potential_documents  = {}
    for term in query_terms:
        if vocab_idf_vales[term] == 0:
            continue
        tf_idf_by_doc = get_tf_dictionary(term)
        idf_values = get_idf_value(term)
        
        for document in tf_idf_by_doc:
            if document not in potential_documents:
                potential_documents[document] = tf_idf_by_doc[document] * idf_values
            potential_documents[document] += tf_idf_by_doc[document] * idf_values
        
    # print(potential_documents)

    for document in potential_documents:
        potential_documents[document] = potential_documents[document] / len(query_terms)
        
    potential_documents = dict(sorted(potential_documents.items(), key=lambda item: item[1], reverse=True))
    i=0
    for i, document_index in enumerate(potential_documents):
        if i == 10:
            break
        print('Score:', potential_documents[document_index], 'Document:', documents[int(document_index)])
        
        # for document_index in potential_documents:
        #     print('score: ', potential_documents[document_index], 'Document: ',documents[int(document_index)])

        

query_string = input("Enter your query: ")
# query_string = "Given an array of positive integers nums, return the maximum possible sum of an ascending subarray in nums.A subarray is defined as a contiguous sequence of numbers in an array."
# query_string = remove_stop_words(query_string)


print(query_string)
query_terms = [term.lower() for term in query_string.strip().split()]
print(query_terms)
calculate_sorted_order_of_documents(query_terms)
# for term in query_terms:
#     print(term, get_idf_value(term))