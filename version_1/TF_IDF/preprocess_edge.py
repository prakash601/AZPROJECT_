import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

# Define the path to the qdata.txt file
file_path = 'version_1/TF_IDF/qdata.txt'
output_file_path = 'version_1/TF_IDF/documents.txt'  # Path to the new output file

# Initialize the NLTK lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Define the custom delimiters for tokenization
custom_delimiters = r'(\(|\)|\[|\]|{|}|,)'

with open('version_1/Question_scrapper/Qdata/index.txt','r') as f:
    index_lines = f.readlines()

# Open the qdata.txt file and create the output file
with open(file_path, 'r') as file, open(output_file_path, 'w') as output_file:
    lines = file.readlines()
    for line, index_line in zip(lines, index_lines): 
        line= index_line.rstrip('\n') + ' ' + line 
        line = line.strip()

        # Tokenize the line using custom delimiters and punctuation marks
        tokens = nltk.word_tokenize(line.lower())

        # Remove punctuation tokens
        tokens = [token for token in tokens if token.isalnum()]

        # Remove stopwords
        tokens = [token for token in tokens if token not in stop_words]

        # Lemmatize the words
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]

        # Write the modified line to the output file
        output_file.write(' '.join(lemmatized_tokens) + '\n')
        # print(' '.join(lemmatized_tokens) + '\n')
