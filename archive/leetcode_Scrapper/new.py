
#all the links of the problems of all tags 

# Import required packages
import os
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

# URL of the inspected page
page_URL = "https://leetcode.com/problemset/all/"  # Replace with the actual URL

def get_links(url):
    driver.get(url)
    time.sleep(6)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all <a> elements with class "inline-flex items-center"
    links = soup.find_all('a', class_="inline-flex items-center")

    # Extract the URLs from the href attributes
    urls = [link['href'] for link in links]
    return urls


links = get_links(page_URL)

tag = []

# Print the extracted links
for link in links:
    tag.append("https://leetcode.com"+str(link))
    # print(link)
#print(tag)
print(len(tag))


#------------------

def get_a_tags(url):
    driver.get(url)
    time.sleep(5)
    links = driver.find_elements(By.TAG_NAME, "a")
    ans = []
    for i in links:
        try:
            # Check if '/problems/' is in the href of the 'a' element
            if "/problems/" in i.get_attribute("href"):
                # If it is, append it to the list of links
                ans.append(i.get_attribute("href"))
        except:
            pass
    print(len(ans))
    return ans
my_ans = []
ass = []
for link in tag:
    my_ans += (get_a_tags(link))
    my_ans = list(set(my_ans))
    print(len(my_ans))
    

# Remove any duplicates that might have been introduced in the process
print(len(my_ans))
my_ans = list(set(my_ans))
print("new")

 
with open('lc_links_clean.txt', 'w') as f: 
    # Iterate over each link in your final list of links
    for link in my_ans:
        # Write each link to the file, followed by a newline
        f.write(link + "\n")
        


# Close the browser
driver.quit()
