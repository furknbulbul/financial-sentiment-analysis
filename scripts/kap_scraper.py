from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
import pandas as pd
from  datetime import date
import time


WEBSITE_URL = "https://www.kap.org.tr"
BASE_URL = "https://www.kap.org.tr/tr/bist-sirketler"
STOCK_NAME = "astor"

"""
MOSTLY DONE, TO BE COMPLETED LATER IF WE NEED IT
"""

OLDEST_DATE= date(2023, 6, 1)

driver = webdriver.Chrome()
driver.get(BASE_URL)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
wait = WebDriverWait(driver, 10)

result = []

def open_stock_page():
    stock_cards = soup.find_all("div", class_ = 'w-clearfix w-inline-block comp-row')
    
    for stock_card in stock_cards:
        temp_div = stock_card.find("a", class_ = "vcell")
        stock_name = temp_div.text
        if stock_name.lower() == STOCK_NAME.lower():
            driver.get(WEBSITE_URL + temp_div['href'])
             
    return None

def open_news():
    
    element = driver.find_element(By.XPATH, "//a[@class='w-inline-block tab-subpage2 not _01']")
    driver.execute_script("arguments[0].click();", element)
    time.sleep(1)
    
    x = driver.find_element(By.XPATH, "//input[@class='checkbox focusable']")
    driver.execute_script("arguments[0].click();", x)
    time.sleep(1)
    getir_button = driver.find_element(By.CLASS_NAME, "filter-button2")
    driver.execute_script("arguments[0].click();", getir_button)
    time.sleep(1)

def open_details():
    rows = driver.find_elements(By.CLASS_NAME, 'disclosureSelectionArea')
    k = 0
    for row in rows:
        k += 1
        if k > 3:
            break

        driver.execute_script("arguments[0].click();", row)
        time.sleep(1)
        modal_content_div  = wait.until(EC.presence_of_element_located((By.ID, 'disclosureContent')))
        #modal_content_div = driver.find_element(By.CLASS_NAME, 'modal-content')
        header = modal_content_div.find_element(By.TAG_NAME, 'h1').text
        print("Header:", header)

        
        bs4 = BeautifulSoup(driver.page_source, 'lxml')
        outer_paragraph = bs4.find("td", class_ = "taxonomy-context-value-summernote")

        tokens = []
        for i in outer_paragraph.find_all('p'):
            tokens.append(i.text)
            for j in i.find_all('span'):
                tokens.append(j.text)
        


        date_str = bs4.find("div", class_ = "type-medium bi-sky-black").text
        #close_button = driver.find_element(By.CLASS_NAME, 'w-inline-block modal-closebutton')
        #driver.execute_script("arguments[0].click();", close_button)
        time.sleep(2)
        print(tokens)
        print("date:", date_str)
        print("--------------------------------------------------")
        





        



open_stock_page()
open_news()
open_details()
driver.quit()





