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

def scrape_data(url, wait_time=int(os.getenv('WAITING_TIME', 30))):
    logger.info(f"Initiated scraper for link: {url}")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-minimized")
        chrome_options.add_argument("--enable-gpu")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(wait_time)
            
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(wait_time)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if abs(new_height - last_height) <= 0.05 * last_height:
                break
            last_height = new_height

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        logger.info(f"Successfully scraped the data for link: {url}")

        # driver.save_screenshot("screenshot.png")
        driver.quit()

        return soup
    except Exception as e:
        logger.error(f"Error in scraping data: {e}")
        return None
