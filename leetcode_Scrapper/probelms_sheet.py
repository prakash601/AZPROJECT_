import pandas as pd

# Read the data from Qindex.txt and index.txt
with open('leetcode_Scrapper/Qindex.txt', 'r') as q_file:
    q_data = q_file.read().splitlines()

with open('leetcode_Scrapper/index.txt', 'r') as index_file:
    index_data = index_file.read().splitlines()

# Create a DataFrame with the data
data = {'Question Number': q_data, 'Question Name': index_data}
df = pd.DataFrame(data)

# Write the DataFrame to an Excel file
df.to_excel('questions.xlsx', index=False)