from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date
import pandas as pd 

"""
    Bu script investing.com sitesinden bir hisse senedi için haberleri çekmektedir. 
    Kullanmak icin local bilgisayarınızda scripti calistirdiginiz directory de chromedriver.exe dosyasının bulunması gerekiyor.
    sizde bulunan chrome versiyonuyla ayni driveri indirmek icin: https://chromedriver.chromium.org/downloads
    Burada akbank hissesi icin calisiyor.
"""


STOCK_NAME = "google" # hisse senedinin adını yazın, sadece output file olustururken kullanılıyor
BASE_URL = "https://www.investing.com/"
STOCK_NEWS_URL = "https://www.investing.com/equities/google-inc-news/"  # buraya hisse senedinin haberlerinin bulundugu sayfanın urlini yazın, sonuna / koyun

driver = webdriver.Chrome()
driver.get(STOCK_NEWS_URL)

OLDEST_DATE = date(2023, 8, 25)  # hisse senedinin haberlerinin bulundugu sayfada en eski haberin tarihi, bu tarihten eski haberler cekilmez
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')


def compare_date_and_date_str(date_str, date_):
    temp = [int(i) for i in date_str.split()[0].split("-")]
    return date(temp[0],temp[1],temp[2]) > date_


def find_article_cards_on_page(index = None):
    new_url = STOCK_NEWS_URL + str(index) if index else STOCK_NEWS_URL
    
    driver.get(new_url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    article_cards = soup.find_all("li", class_="border-b border-[#E6E9EB] first:border-t last:border-0")
    if article_cards == []:
        return [], False
    
    articles = []
    for article_card in article_cards:
        article_link = article_card.find("a", class_="inline-block text-sm leading-5 sm:text-base sm:leading-6 md:text-lg md:leading-7 font-bold mb-2 hover:underline")
        article_headline = article_link.text
        try:
            article_url = article_link["href"]
        except:
            article_url = ""
        article_publish_date = article_card.find("time", class_="ml-2")['datetime']
        article =  {"headline": article_headline,
            "url": article_url,
            #"writer_name": article_writer_name,
            # "writer_profile": article_writer_profile,
            "publish_date": article_publish_date
        }
        articles.append(article)
       
        
    
    return articles, compare_date_and_date_str(articles[-1]['publish_date'], OLDEST_DATE)


def get_articles():
    articles = []
    page_index = 1
    while True:
        new_articles, is_new = find_article_cards_on_page(page_index)
        articles.extend(new_articles)
        if not is_new:
            break
        page_index += 1
    return articles    





def get_article_text(article_url):
    try:
        url = BASE_URL + article_url
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        article_page = soup.find("div", class_="WYSIWYG articlePage")
        if article_page is None:
            return ""
        tokens = []
        for i in article_page.find_all("p"):
            if "Pozisyon"  not in i.text and "Position" not in i.text: #anlamadığım bir şekilde pozisyon ... yazısı çıkıyor onu engellemek için 
                tokens.append(i.text)
                temp = i.find_all("span", class_ = "aqPopupWrapper js-hover-me-wrapper")
                if temp is not None and len(temp) > 0:
                    for j in temp:
                        tokens.append(j.text)
        return " ".join(tokens)
    except:
        return None
        
   

def get_all_article_texts(articles):
    article_texts = []
    error_count = 0
    for article in articles:
        article_text = get_article_text(article['url'])
        if article_text is None:
            error_count += 1
            if error_count > 10:
                break
            continue
        article["text"] = article_text
        article_texts.append(article)
    return article_texts

articles = get_articles()
article_texts = get_all_article_texts(articles)

df = pd.DataFrame(article_texts)
df.to_excel(f"{STOCK_NAME}.xlsx")
    
driver.quit()






