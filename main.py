import requests
import re
import os
import json
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from link_retriever_agent import retrieve_room_link
from data_retriever_agent import retrieve_room_data
from scrapper import scrape_data
from logger_config import logger
from save_data import save
from process_data import process
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

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
        return set()

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
        
    text = soup.get_text(separator=' ', strip=True)
    logger.debug("Retrieved page data: ")
    logger.debug(text)
    return text

def main(base_url):
    logger.info(f"Starting main process for base URL: {base_url}")
    
    data_to_save = {'URL_Scrapped': base_url}
    note = "Process initiated"
    
    soup = scrape_data(base_url)
    if not soup:
        note = "Initial page scraping failed"
        logger.error(note)
        save([{**data_to_save, 'Note': note}])
        return
    
    unique_urls = get_unique_urls(soup, base_url)
    if not unique_urls:
        note = "No unique URLs found"
        logger.error(note)
        save([{**data_to_save, 'Note': note}])
        return
    
    link = retrieve_room_link(unique_urls)
    if not link:
        note = "Room link retrieval failed"
        logger.error(note)
        save([{**data_to_save, 'Note': note}])
        return
    
    data_to_save['URL_Scrapped'] = link
    note = "Room link retrieved successfully"
    
    room_page_soup = scrape_data(link)
    if not room_page_soup:
        note = "Room page scraping failed"
        logger.error(note)
        save([{**data_to_save, 'Note': note}])
        return
    
    room_page_text = process_room_soup(room_page_soup)
    room_details = get_room_details(room_page_text)
    if not room_details:
        note = "Room details retrieval failed"
        logger.error(note)
        save([{**data_to_save, 'Note': note}])
        return
    
    # Add this debugging line
    logger.debug(f"Room details: {room_details}")

    # Modify this part
    if isinstance(room_details, list):
        for item in room_details:
            if isinstance(item, tuple) and len(item) == 2:
                key, value = item
                data_to_save[key] = value
            else:
                logger.warning(f"Unexpected item in room_details: {item}")
    else:
        logger.error(f"Unexpected type for room_details: {type(room_details)}")
        note = "Room details in unexpected format"
        save([{**data_to_save, 'Note': note}])
        return
    
    note = "Room details retrieved successfully"
    
    processed_data = process(json.dumps(room_details), link)
    if not processed_data:
        note = "Data processing failed"
        logger.error(note)
        save([{**data_to_save, 'Note': note}])
        return
    
    note = "Data processed successfully"
    
    # Save processed data
    if save([{**item, 'Note': note} for item in processed_data]):
        logger.info("Successfully saved processed data")
        return True
    else:
        note = "Processed data saving failed"
        logger.error(note)
        save([{**data_to_save, 'Note': note}])
        return

def process_websites(csv_path, max_workers=int(os.getenv('MAX_WORKERS', 5))):
    logger.info(f"Starting to process websites from {csv_path}")
    
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        websites = [row['websites'] for row in reader if 'websites' in row]
    
    logger.info(f"Found {len(websites)} websites to process")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(main, url): url for url in websites}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
                logger.info(f"Completed processing for {url}")
            except Exception as exc:
                logger.error(f"Processing for {url} generated an exception: {exc}")
    
    # for url in websites:
    #     main(url)

if __name__ == "__main__":
    csv_path = 'data/websites.csv'
    process_websites(csv_path)
