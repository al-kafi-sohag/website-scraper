import requests
import re
import json
from bs4 import BeautifulSoup
from link_retriever_agent import retrieve_room_link
from data_retriever_agent import retrieve_room_data
from logger_config import logger

def scrape_data(url):
    logger.info(f"Initiated scraper for link: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"Successfully scraped the data for link: {url}")
            return soup
        else:
            logger.error(f"Failed to retrieve content. Status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error in scraping data: {e}")
        return None

def get_unique_urls(soup, base_url):
    logger.info("Initiating URL collection")
    base_url = base_url.rstrip('/')  # Remove trailing slash once
    unique_urls = set()
    
    try:
        for link in soup.find_all('a', href=True):
            href = link['href'].lstrip('/')  # Remove leading slash if present
            
            if not href.startswith(('http://', 'https://')):
                href = f"{base_url}/{href}"
            
            if href.startswith(base_url):
                unique_urls.add(href)
        
        logger.info(f"Collected URLs successfully. Unique URLs found: {len(unique_urls)}")
        
        logger.debug("Pretty-printed JSON result:")
        logger.debug(json.dumps(list(unique_urls), indent=2, ensure_ascii=False))
        
        return unique_urls
    except Exception as e:
        logger.error(f"Failed to collect URLs: {e}")
        return set()  # Return an empty set in case of error

def get_room_details(text):
    logger.info("Initiated collecting room details")
    try:
        response = retrieve_room_data(text)
        return response
    except Exception as e:
        logger.error(f"Error in retrieving room details: {e}")
        return None

def process_room_soup(soup):
    logger.info("Processing room soup")
    for tag in soup(["head", "script", "style", "input", "textarea", "iframe", "noscript", "svg", "img", "br"]):
        tag.decompose()
        
    text = soup.get_text()
    
    # Remove extra whitespace and blank lines
    lines = (line.strip() for line in text.splitlines())
    text = '\n'.join(line for line in lines if line)
    
    # Remove any remaining HTML tags
    text = re.sub('<[^<]+?>', '', text)
    logger.debug(f"Processed text: {text[:100]}...")  # Log first 500 characters
    return text

def main(base_url):
    logger.info(f"Starting main process for base URL: {base_url}")
    soup = scrape_data(base_url)
    if soup:
        unique_urls = get_unique_urls(soup, base_url)
        link = retrieve_room_link(unique_urls)
        if link:
            room_page_soup = scrape_data(link)
            if room_page_soup:
                room_page_text = process_room_soup(room_page_soup)
                room_details = get_room_details(room_page_text)
                if room_details:
                    logger.info("Successfully completed the scraping process")
                else:
                    logger.error("Failed to retrieve room details")
            else:
                logger.error("Failed to scrape room page")
        else:
            logger.error("Failed to retrieve room link")
    else:
        logger.error("Failed to scrape initial page")

if __name__ == "__main__":
    main('https://www.tonsofrentals.com')
