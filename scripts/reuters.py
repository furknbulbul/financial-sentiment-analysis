from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import openpyxl

# Initialize the Excel workbook and worksheet
workbook = openpyxl.Workbook()
worksheet = workbook.active

# Set the headers in the first row
worksheet.append(['Headline', 'Date', 'Article Text'])

# Initialize the Chrome WebDriver
driver = webdriver.Chrome('chromedriver.exe')

# Define the URL of the Reuters archive page
url = 'https://www.reuters.com/company/google-llc/?view=page&page=5&pageSize=10'
driver.get(url)

# Initialize a list to store scraped data
data = []

# Define the number of times to load more content
load_more_iterations = 500

# Initialize a flag to check if there is more content to load
more_content = True

# Loop to load more content and scrape data
for _ in range(load_more_iterations):
    try:
        # Find all news headlines
        news_headlines = driver.find_elements(By.CLASS_NAME, "text__text__1FZLe.text__dark-grey__3Ml43.text__medium__1kbOh.text__heading_6__1qUJ5.heading__base__2T28j.heading__heading_6__RtD9P")

        # Collect links to the articles without navigating away using the CSS selector
        article_links = driver.find_elements(By.CSS_SELECTOR, "#fusion-app > div.search-layout__body__1FDkI > div.search-layout__main__L267c > div > div.search-results__sectionContainer__34n_c > ul > li > div > div.media-story-card__placement-container__1R55- > a")

        # Loop through each headline and gather links
        for headline, article_link in zip(news_headlines, article_links):
            # Get the headline text
            headline_text = headline.text

            # Get the article link
            article_url = article_link.get_attribute("href")

            # Append the data to the list
            data.append([headline_text, article_url])

        # Find the "Next" button for loading more content using a CSS selector
        load_more_button = driver.find_element(By.CSS_SELECTOR, '#fusion-app > div.search-layout__body__1FDkI > div.search-layout__main__L267c > div > div.search-results__pagination__2h60k > button:nth-child(3)').click()

        # Wait for the page to load
        time.sleep(3)


        # Check if there is a "Next" button on the page
        next_button = driver.find_element(By.CSS_SELECTOR, '#fusion-app > div.search-layout__body__1FDkI > div.search-layout__main__L267c > div > div.search-results__pagination__2h60k > button:nth-child(3)')
        
        if "disabled" in next_button.get_attribute("class"):
            # The button is disabled, break the loop
            more_content = False
            break  # Break out of the loop

        print("Clicked!!")

    except Exception as e:
        print(e)
        break

    # If there is no more content to load, exit the loop
    if not more_content:
        break
# Loop through the collected article links and scrape data
for headline_text, article_url in data:
    try:
        driver.get(article_url)
        time.sleep(2)  # Adjust the sleep time as needed

        # Gather the data from the article page
        date = driver.find_element(By.CLASS_NAME, "article-header__dateline__4jE04").text
        article_text = driver.find_element(By.CSS_SELECTOR, "#main-content > article > div.article__main__33WV2 > div > header > div > div > h1").text

        # Append the data to the Excel worksheet
        worksheet.append([headline_text, date, article_text])

    except Exception as e:
        print(e)

# Save the Excel workbook
workbook.save('scraped_data.xlsx')

# Close the WebDriver
driver.quit()