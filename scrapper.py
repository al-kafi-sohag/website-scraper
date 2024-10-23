import time
import os
from bs4 import BeautifulSoup
from logger_config import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

load_dotenv()

def scrape_data(url):
    logger.info(f"Initiated scraper for link: {url}")
    try:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Wait for new content to load
        time.sleep(int(os.getenv('WAITING_TIME', 30)))
            
        # Scroll to the bottom until no new content is loaded
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(10)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Get the page source after scrolling
        page_source = driver.page_source

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        logger.info(f"Successfully scraped the data for link: {url}")

        # Close the browser
        # driver.save_screenshot("screenshot.png")
        driver.quit()

        return soup
    except Exception as e:
        logger.error(f"Error in scraping data: {e}")
        return None
