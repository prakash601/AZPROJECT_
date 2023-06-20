import math
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

with open('version_1/Question_scrapper/Qdata/index.txt', 'r') as f:
    lines = f.readlines()

index_terms = []
for line in lines:
    terms = line.strip().split(' ')
    index_terms.extend(terms)

astop_words = set(stopwords.words('english'))
custom_stop_words = ['<', '<=', '=', '<', '>=', 'r', ',', ']', '.', '[', '(', ')', '+', '-', 'return', 'given', '--', '//', '/', '*', '**', '**=', '*=', '+=', '-=', '==', '!=', '!=', '+=', '-=', '*=', '/=', '%=', '||', '!', '&&', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '>>=', '<<=', '!', '@', '#', '$', '%', '&', '*', '(', ')', '-', '+', '=', '[', ']', '{', '}', '|', '\\', '/', '~', '^', '>', '<', '.', ',', ':', ';', '"', "'", '_', '?', '`', '``', '````', '``````', '````````', '``````````', '```````````', '````````````', '`````````````', '``````````````', '```````````````', '````````````````', '`````````````````', '``````````````````', '```````````````````', '``']

stop_words = astop_words.union(custom_stop_words)


def remove_stop_words(text):
    words = regexp_tokenize(text, pattern=r"\w+|[^\w\s]|\(|\)|\[|\]|{|}|,|\.|\+|-|:|\"|&|\*|/|=|#")
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)


def preprocess(document_text):
    filtered_terms = remove_stop_words(document_text).strip().split()
    lemmatized_terms = [lemmatizer.lemmatize(term.lower()) for term in filtered_terms]
    # weighted_terms = []
    # for term in lemmatized_terms:
    #     if term in index_terms:
    #         # Assign a higher weight to terms in index_terms
    #         weighted_terms.append(term + '^10')  # You can customize the weight here
    #     else:
    #         weighted_terms.append(term)
    return lemmatized_terms


vocab = {}
documents = []

with open('version_1/Question_scrapper/Qdata/index.txt','r') as f:
    index_lines = f.readlines()

file_path = 'version_1/TF_IDF/qdata.txt'

with open(file_path, 'r') as file:
    lines = file.readlines()
    for line, index_line in zip(lines, index_lines): 
        line= index_line.rstrip('\n') + ' ' + line 
        line = ''.join(line)  # Combine all lines into a single string
        tokens = preprocess(line)
        # print(line)
        documents.append(tokens)
        token_set = set(tokens)
        for token in token_set:
            vocab[token] = vocab.get(token, 0) + 1

vocab = {k: v for k, v in sorted(vocab.items(), key=lambda item: item[1], reverse=True)}



print('numner of documents', len(documents))
print('size of vocab', len(vocab))
print('sample document', documents[0])
print(vocab)   
# Save the vocab in a text file
with open('version_1/TF_IDF/vocab.txt', 'w') as f:
    for key in vocab.keys():
        f.write("%s\n" % key)

with open('version_1/TF_IDF/idf-values.txt', 'w') as f:
    for key in vocab.keys():
        f.write("%s\n" % vocab[key])

# Save the documents in a text file
with open('version_1/TF_IDF/documents_tfidf.txt', 'w') as f:
    for doc in documents:
        f.write("%s\n" % ' '.join(doc))

inverted_index = {}
for index, doc in enumerate(documents):
    for token in set(doc):
        if token not in inverted_index:
            inverted_index[token] = [index]
        else:
            inverted_index[token].append(index)

# Save the inverted index in a text file
with open('version_1/TF_IDF/inverted_index_tfidf.txt', 'w') as f:
    for key in inverted_index.keys():
        f.write("%s\n" % key)
        f.write("%s\n" % ' '.join([str(x) for x in inverted_index[key]]))




# #read the index.txt and prepare document, vocab ,idf
# import math
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import regexp_tokenize
# from nltk.stem import WordNetLemmatizer

# lemmatizer = WordNetLemmatizer()
# # nltk.download('stopwords')
# # nltk.download('wordnet') 

# with open('leetcode_Scrapper/index.txt','r') as f:
#     lines = f.readlines()
    
# # index_terms = [term.strip() for term in lines]
# index_terms = []
# for line in lines:
#     terms = line.strip().split(' ')
#     index_terms.extend(terms)

# # print(index_terms)

# # def perprocess_qdata(document_text):
# #     tokens = word_tokenize(document_text.strip())
# #     return tokens
    
# astop_words = set(stopwords.words('english'))
# custom_stop_words = ['<','<=', '=', '<', '>=','r', ',',']','.','[','(',')','+','-','return','given','--','//','/','*','**','**=','*=','+=','-=','==','!=','!=','+=','-=','*=','/=','%=', '||', '!', '&&', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '>>=', '<<=','!', '@', '#', '$', '%', '&', '*', '(', ')', '-', '+', '=', '[', ']', '{', '}', '|',
#     '\\', '/', '~', '^', '>', '<', '.', ',', ':', ';', '"', "'", '_', '?','`','``','````','``````','````````','``````````','```````````','````````````','`````````````','``````````````','```````````````','````````````````','`````````````````','``````````````````','```````````````````', '``',
#     'the', 'was', 'were',
#      'during', 'since',  'unless', 
#     ',', 'how', 'are', 'you', '?', '(', "I'm", 'doing', 'well', ')', '[',  'you', ']', '{', 'Nice',  'meet', 'you', '}', '&', '(', '...', ')', ',', '[', '..', ':', ']', '....', '+-----------------+----------+|', '|+-----------------+----------+|', '|+-----------------+----------+', '"||**||**|*"', '", "', '=#', ',', '#,', '#,#"', ',', ',', ':"../"', ').', '"./"', '/"'

#  ]
# stop_words = astop_words.union(custom_stop_words)

# def remove_stop_words(text):
#     words = regexp_tokenize(text, pattern=r"\w+|[^\w\s]|\(|\)|\[|\]|{|}|,|\.|\+|-|:|\"|&|\*|/|=|#")
#     # words = text.split()
#     filtered_words = [word for word in words if word.lower() not in stop_words]
#     return ' '.join(filtered_words)

    
# def preprocess(document_text):
#     filtered_terms = remove_stop_words(document_text).strip().split()
#     lemmatized_terms = [lemmatizer.lemmatize(term.lower()) for term in filtered_terms]
#     weighted_terms = []
#     for term in lemmatized_terms:
#         if term in index_terms:
#             # Assign a higher weight to terms in index_terms
#             weighted_terms.append(term + '^10')  # You can customize the weight here
#         else:
#             weighted_terms.append(term)
#     return weighted_terms


# vocab = {}
# documents = []



# for index,line in enumerate(lines, start = 1):
#     file_path = f'version_1/Question_scrapper/Qdata/{index}/{index}.txt'
#     with open(file_path,'r') as f:
#         file_lines = f.readlines()
        
#     for i in file_lines:
#         current_line = i.strip()
#         line += current_line
        
#     tokens = preprocess(line)
#     documents.append(tokens)
#     token = set(tokens)
#     for token in tokens:
#         if token not in vocab:
#             vocab[token] = 1
#         else:
#             vocab[token] += 1

# vocab  = {k: v for k, v in sorted(vocab.items(), key=lambda item: item[1], reverse=True)}

# print('numner of documents', len(documents))
# print('size of vocab', len(vocab))
# print('sample document', documents[0])
# print(vocab)    

# # print(documents[:10])
    
# # save the vocab in a text file
# with open('TF_IDF/vocab.txt','w') as f:
#     for key in vocab.keys():
#         f.write("%s\n" % key)

# with open('TF_IDF/idf-values.txt','w') as f:
#     for key in vocab.keys():
#         f.write("%s\n" % vocab[key])

# #save the documents in a text file
# with open('TF_IDF/documents_tfidf.txt','w') as f:
#     for doc in documents:
#         f.write("%s\n" % ' '.join(doc))
        
# inverted_index = {}
# for index, doc in enumerate(documents):
#     for token in doc:
#         if token not in inverted_index:
#             inverted_index[token] = [index]
#         else:
#             inverted_index[token].append(index)

# # save the inverted index in a text file
# with open('TF_IDF/inverted_index_tfidf.txt','w') as f:
#     for key in inverted_index.keys():
#         f.write("%s\n" % key)
#         f.write("%s\n" % ' '.join([str(x) for x in inverted_index[key]]))