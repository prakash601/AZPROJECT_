# Import required packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup



# Define the chromedriver service
s = Service('chromedriver.exe')

# Instantiate the webdriver
driver = webdriver.Chrome(service=s)



# Open the LeetCode problems page
driver.get('https://leetcode.com/problemset/all/?page=')

# Get the page source
page_source = driver.page_source

# Create a BeautifulSoup object
soup = BeautifulSoup(page_source, 'html.parser')
# Find all <a> elements with class "reactable-pagination a"
problem_links = soup.find_all('a', class_="reactable-pagination a")

# Extract the URLs from the href attributes

urls = [link['href'] for link in problem_links]


for url in urls:
    print(url)
# Close the Selenium driver
driver.quit()
