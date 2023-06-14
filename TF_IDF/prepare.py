#read the index.txt and prepare document, vocab ,idf
import math
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


with open('leetcode_Scrapper/index.txt','r') as f:
    lines = f.readlines()


# def perprocess_qdata(document_text):
#     tokens = word_tokenize(document_text.strip())
#     return tokens
    

def preprocess(document_text):
    #remove the leading number from the string, remove not alpha numeric character, make everything lower case
    # print(docment_text)
    terms = [term.lower() for term in document_text.strip().split()[1:] ]
    # terms = word_tokenize(document_text.strip())[1:]
    # print(terms)
    return terms
    
    
vocab = {}
documents = []

for index,line in enumerate(lines, start = 1):
    print(index)
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
    documents.append(tokens)
    token = set(tokens)
    for token in tokens:
        if token not in vocab:
            vocab[token] = 1
        else:
            vocab[token] += 1

#reverse sort the vocab based on the value
vocab  = {k: v for k, v in sorted(vocab.items(), key=lambda item: item[1], reverse=True)}

print('numner of documents', len(documents))
print('size of vocab', len(vocab))
print('sample document', documents[0])
print(vocab)    

# print(documents[:10])
    
#save the vocab in a text file
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

#save the inverted index in a text file
with open('TF_IDF/inverted_index.txt','w') as f:
    for key in inverted_index.keys():
        f.write("%s\n" % key)
        f.write("%s\n" % ' '.join([str(x) for x in inverted_index[key]]))