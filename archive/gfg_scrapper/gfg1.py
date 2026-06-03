# for unlocked problems of all tags 

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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


# Define the chromedriver service
s = Service('chromedriver.exe')

# Instantiate the webdriver
driver = webdriver.Chrome(service=s) 

# URL of the inspected page
page_URL = "https://practice.geeksforgeeks.org/explore?page=7&sortBy=submissions&utm_source=geeksforgeeks&utm_medium=main_header&utm_campaign=practice_header"  # Replace with the actual URL

driver.get("https://practice.geeksforgeeks.org/explore?page=1&sortBy=submissions&utm_source=geeksforgeeks&utm_medium=main_header&utm_campaign=practice_header")

# Scroll down to load all the problems


while True:
    # Scroll to the bottom of the page
    # driver.find_element_by_tag_name("a").send_keys(Keys.END)
    driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.END)
    time.sleep(2)  # Wait for the page to load

    # Check if more elements with tag name 'a' (links) are loaded
    try:
        driver.find_element(By.TAG_NAME, "a")
    except NoSuchElementException:
        break  # Stop scrolling if no more links are loaded


#------------------
def get_a_tags(url):
    # Load the URL in the browser
    # driver.get(url)
    # Wait for 7 seconds to ensure the page is fully loaded
    # time.sleep(7)
    # Find all the 'a' elements on the page
    links = driver.find_elements(By.TAG_NAME, "a")
    ans = []
    # Iterate over each 'a' element
    for i in links:
        try:
            # Check if '/problems/' is in the href of the 'a' element
            if "/problems/" in i.get_attribute("href"):
                # If it is, append it to the list of links
                ans.append(i.get_attribute("href"))
        except:
            pass
    # Remove duplicate links using set
    ans = list(set(ans))
    return ans

my_ans = []


my_ans = get_a_tags(page_URL)
# Remove any duplicates that might have been introduced in the process
print(len(my_ans))
my_ans = list(set(my_ans))
print(my_ans)

 
# with open('lc_links_clean_unloacked.txt', 'w') as f: 
#     # Iterate over each link in your final list of links
#     for link in my_ans:
#         # Write each link to the file, followed by a newline
#         f.write(link + "\n")
        


# Close the browser
driver.quit()
