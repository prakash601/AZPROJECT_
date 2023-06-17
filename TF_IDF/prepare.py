#read the index.txt and prepare document, vocab ,idf
import math
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
nltk.download('stopwords')
nltk.download('wordnet') 

with open('leetcode_Scrapper/index.txt','r') as f:
    lines = f.readlines()
    
index_terms = [term.strip() for term in lines]

# def perprocess_qdata(document_text):
#     tokens = word_tokenize(document_text.strip())
#     return tokens
    
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

# def preprocess(document_text):
#     #remove the leading number from the string, remove not alpha numeric character, make everything lower case
#     # print(docment_text)
#     # terms = [term.lower() for term in remove_stop_words(document_text).strip().split()[1:] ]
#     terms = [stemmer.stem(term.lower()) for term in remove_stop_words(document_text).strip().split()[1:]]

#     # terms = word_tokenize(document_text.strip())[1:]
#     # print(terms)
#     return terms
    
def preprocess(document_text):
    filtered_terms = remove_stop_words(document_text).strip().split()[1:]
    lemmatized_terms = [lemmatizer.lemmatize(term.lower()) for term in filtered_terms]
    weighted_terms = []
    for term in lemmatized_terms:
        if term in index_terms:
            # Assign a higher weight to terms in index_terms
            weighted_terms.append(term + '^5')  # You can customize the weight here
        else:
            weighted_terms.append(term)

    return weighted_terms


vocab = {}
documents = []

document_first_line = []

for index,line in enumerate(lines, start = 1):
    # print(index)
    #read statement from txt file name index.txt and add it to the line 
    file_path = f'leetcode_Scrapper/Qdata/{index}/{index}.txt'
    with open(file_path,'r') as f:
        file_lines = f.readlines()
    line = ''
    for i in file_lines:
        current_line = i.strip()
        if "Example" in current_line:
            break
        line += current_line
    document_first_line.append(line.rstrip())
        
# document_first_line = '\n'.join(document_first_line)
# print(document_first_line)
# for line in document_first_line:
#     print(line)
#save the documents in a text file
with open('TF_IDF/documents_txt.txt','w') as f:
    for doc in document_first_line:
        f.write("%s\n" % (doc))


for index,line in enumerate(lines, start = 1):
    # print(index)
    #read statement from txt file name index.txt and add it to the line 
    file_path = f'leetcode_Scrapper/Qdata/{index}/{index}.txt'
    with open(file_path,'r') as f:
        lines = f.readlines()
        
    for i in lines:
        current_line = i.strip()
        if "Example" in current_line:
            break
        line += current_line
        
    tokens = preprocess(line)
    # break
    documents.append(tokens)
    token = set(tokens)
    for token in tokens:
        if token not in vocab:
            vocab[token] = 1
        else:
            vocab[token] += 1

#reverse sort the vocab based on the value
vocab  = {k: v for k, v in sorted(vocab.items(), key=lambda item: item[1], reverse=True)}

# print('numner of documents', len(documents))
# print('size of vocab', len(vocab))
# print('sample document', documents[0])
# print(vocab)    

# print(documents[:10])
    
# save the vocab in a text file
with open('TF_IDF/vocab.txt','w') as f:
    for key in vocab.keys():
        f.write("%s\n" % key)

with open('TF_IDF/idf-values.txt','w') as f:
    for key in vocab.keys():
        f.write("%s\n" % vocab[key])

#save the documents in a text file
with open('TF_IDF/documents.txt','w') as f:
    for doc in documents:
        f.write("%s\n" % ' '.join(doc))
        
inverted_index = {}
for index, doc in enumerate(documents):
    for token in doc:
        if token not in inverted_index:
            inverted_index[token] = [index]
        else:
            inverted_index[token].append(index)

# save the inverted index in a text file
with open('TF_IDF/inverted_index.txt','w') as f:
    for key in inverted_index.keys():
        f.write("%s\n" % key)
        f.write("%s\n" % ' '.join([str(x) for x in inverted_index[key]]))