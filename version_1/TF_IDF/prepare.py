from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import pickle



# Load and preprocess documents
# preprocessed_documents  = [
#     "This is the first document.",
#     "This document is the second document.",
#     "And this is the third one.",
#     "Is this the first document?"
# ]

output_file_path = 'version_1/TF_IDF/documents.txt' 
with open(output_file_path, 'r') as f:
    preprocessed_documents = f.readlines()
    


# preprocessed_documents = [preprocess(doc) for doc in documents]

# Calculate TF-IDF values and save to file
vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'), tokenizer=None)
tfidf_matrix = vectorizer.fit_transform(preprocessed_documents)


# Save TF-IDF matrix to file
with open('tfidf_matrix.pkl', 'wb') as file:
    pickle.dump(tfidf_matrix, file)

with open('vectorizer.pkl', 'wb') as file:
    pickle.dump(vectorizer, file)

# Query and rank documents
preprocessed_query = "linked list"
# preprocessed_query = preprocess(query)
query_vector = vectorizer.transform([preprocessed_query])
similarity_scores = cosine_similarity(query_vector, tfidf_matrix)
sorted_indices = similarity_scores.argsort()[0][::-1]

# Print ranked documents
for index in sorted_indices:
    print(f"Document: {preprocessed_documents[index]}, Similarity Score: {similarity_scores[0][index]}")
    

# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import TfidfVectorizer
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# import pickle
# from annoy import AnnoyIndex

# # Load and preprocess documents
# output_file_path = 'version_1/TF_IDF/documents.txt' 
# with open(output_file_path, 'r') as f:
#     preprocessed_documents = f.readlines()

# # Calculate TF-IDF values and save to file
# vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'), tokenizer=None)
# tfidf_matrix = vectorizer.fit_transform(preprocessed_documents)

# # Save TF-IDF matrix to file
# with open('tfidf_matrix.pkl', 'wb') as file:
#     pickle.dump(tfidf_matrix, file)

# # Build the ANN index
# num_dimensions = tfidf_matrix.shape[1]
# ann_index = AnnoyIndex(num_dimensions, 'angular')  # Use angular distance metric for cosine similarity
# for i in range(tfidf_matrix.shape[0]):
#     vector = tfidf_matrix[i].toarray().flatten()
#     ann_index.add_item(i, vector)
# ann_index.build(10)  # Build the index with 10 trees (adjust this value based on your data)

# # Query and rank documents
# preprocessed_query = "linked list"
# query_vector = vectorizer.transform([preprocessed_query])
# query_vector = query_vector.toarray().flatten()

# # Perform approximate nearest neighbor search
# num_results = 10
# nearest_indices = ann_index.get_nns_by_vector(query_vector, num_results)

# # Print ranked documents
# for index in nearest_indices:
#     similarity_score = cosine_similarity(query_vector.reshape(1, -1), tfidf_matrix[index])[0][0]
#     print(f"Document: {preprocessed_documents[index]}, Similarity Score: {similarity_score}")




   
   
   
   
   
   
   
   
   
   
   
   
   
   
    
# index_terms = [term.strip() for term in lines]
# index_terms = []
# for line in lines:
#     terms = line.strip().split(' ')
#     index_terms.extend(terms)

# print(index_terms)

# def perprocess_qdata(document_text):
#     tokens = word_tokenize(document_text.strip())
#     return tokens

    # weighted_terms = []
# def preprocess(document_text):
#     filtered_terms = (document_text).strip().split()
#     weighted_terms = []
#     for term in filtered_terms:
#         if term in index_terms:
#             weighted_terms.append(term + '^10')  # You can customize the weight here
#         else:
#             weighted_terms.append(term)
#     return weighted_terms




        





# with open('TF_IDF/vocab.txt','w') as f:
#     for key in vocab.keys():
#         f.write("%s\n" % key)

# with open('TF_IDF/idf-values.txt','w') as f:
#     for key in vocab.keys():
#         f.write("%s\n" % vocab[key])

# #save the documents in a text file
# with open('TF_IDF/documents.txt','w') as f:
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
# with open('TF_IDF/inverted_index.txt','w') as f:
#     for key in inverted_index.keys():
#         f.write("%s\n" % key)
#         f.write("%s\n" % ' '.join([str(x) for x in inverted_index[key]]))