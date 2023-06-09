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

# The base URL for the pages to scrape
page_URL = "https://leetcode.com/tag/array/"



def get_a_tags(url):
    driver.get(url)
    time.sleep(10)
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
    return ans

my_ans = []
for link in links:
for i in range(1, 55):
    my_ans += (get_a_tags(page_URL+str(i)))

# Remove any duplicates that might have been introduced in the process
my_ans = list(set(my_ans))
my_ans = []

my_ans = get_a_tags("https://leetcode.com/tag/array/")

print(len(my_ans))
print(my_ans)
print(len(my_ans))

# Close the browser
driver.quit()
