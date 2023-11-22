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
STOCK_NAME = "arclk"



OLDEST_DATE= date(2023, 8, 1)

driver = webdriver.Chrome()
driver.get(BASE_URL)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
wait = WebDriverWait(driver, 10)

result = []

def compare_date_and_date_str(date_str, date_):
    temp = [int(i) for i in date_str.split()[0].split(".")]
    return date(temp[2],temp[1],temp[0]) > date_

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
    
    notifications_per_page = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'items-per-page-area')))
    print(notifications_per_page)
    number_buttons = notifications_per_page.find_elements(By.TAG_NAME, 'button')
    _250_button = number_buttons[-1]
    driver.execute_script("arguments[0].click();", _250_button)  # TODO: change 250 news with specific date control

    rows = driver.find_elements(By.CLASS_NAME, 'disclosureSelectionArea')

    index = 0
    while index < len(rows):
        try:
            row = rows[index]
            index += 1
            driver.execute_script("arguments[0].click();", row)
            time.sleep(1)
            modal_content_div  = wait.until(EC.presence_of_element_located((By.ID, 'disclosureContent')))
            header = modal_content_div.find_element(By.TAG_NAME, 'h1').text.split("\n")[0]
            brief_summary = modal_content_div.find_element(By.CLASS_NAME, 'modal-briefsummary')
            temp = brief_summary.find_elements(By.CLASS_NAME, 'type-medium')
            date = temp[0].text.strip()
            
            try:
                details = modal_content_div.find_element(By.CLASS_NAME, 'text-block-value').text
                notification_type = temp[1].text
            except:
                details = None
                notification_type = None

            result.append({"header": header,
                        "date": date,
                        "notification_type": notification_type,
                        "details": details})

            

            close_button = modal_content_div.find_element(By.CLASS_NAME, 'modal-closebutton')
            driver.execute_script("arguments[0].click();", close_button)
        except:
            continue

        # if compare_date_and_date_str(date, OLDEST_DATE):
        #     # click show more button
        #     try:
        #         #button = wait.until(EC.presence_of_element_located((By.CLASS, 'notifications-more-block')))[-1]

        #         button = modal_content_div.find_element(By.CLASS_NAME, 'button-more')
        #         print(button)
        #         driver.execute_script("arguments[0].click();", button)
        #         rows = driver.find_elements(By.CLASS_NAME, 'disclosureSelectionArea')
        #     except:
        #         print("no more button")
        #         break
        # else:
        #     break

    
    return result

    
        
        


open_stock_page()
open_news()
res = open_details()
df = pd.DataFrame(res)
df.to_excel(f"{STOCK_NAME}_kap.xlsx")
print(res)
driver.quit()





