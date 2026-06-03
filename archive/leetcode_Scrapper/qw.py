import requests
from bs4 import BeautifulSoup

# Send a GET request to the webpage
url = "https://practice.geeksforgeeks.org/problems/subarray-with-given-sum-1587115621/1?page=1&sortBy=submissions"  # Replace with the actual URL
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the <div> element with class "problems_problem_content__Xm_eO"
problem_div = soup.find('div', class_='problems_problem_content__Xm_eO')

# Extract the text content
problem_text = problem_div.get_text()

# Print the scraped text
print(problem_text)