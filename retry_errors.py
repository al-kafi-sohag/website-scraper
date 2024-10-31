import csv
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from logger_config import logger
from scrapper import scrape_data
from main import (
    get_unique_urls,
    retrieve_room_link,
    process_room_soup,
    get_room_details
)
from process_data import process
from save_data import save

# Constants for retry configuration
RETRY_WAIT_TIMES = {
    'scraping_error': 15,
    'url_error': 15,
    'data_error': 10
}

MAX_RETRIES = {
    'scraping_error': 1,
    'url_error': 1,
    'data_error': 1
}

DEFAULT_MAX_WORKERS = int(os.getenv('MAX_WORKERS', 5))

def read_error_csv(error_csv_path):
    if not os.path.exists(error_csv_path):
        logger.error(f"Error CSV file not found: {error_csv_path}")
        return []
    
    with open(error_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [(row['URL_Scrapped'], row.get('Note', '')) for row in reader if 'URL_Scrapped' in row]

def categorize_error(note):
    error_categories = {
        'scraping_error': [
            'Initial page scraping failed',
            'Room page scraping failed'
        ],
        'url_error': [
            'No unique URLs found',
            'Room link retrieval failed'
        ],
        'data_error': [
            'Room details retrieval failed',
            'Room details in unexpected format',
            'Data processing failed'
        ],
        'save_error': [
            'Processed data saving failed'
        ],
        'success': [
            'Room link retrieved successfully',
            'Room details retrieved successfully',
            'Data processed successfully'
        ]
    }
    
    for category, patterns in error_categories.items():
        if any(pattern.lower() in note.lower() for pattern in patterns):
            return category
    return 'unknown_error'

def get_room_iframe_src(soup, iframe=None):
    if iframe:
        iframe_tag = soup.find('iframe')
        if iframe_tag and 'src' in iframe_tag.attrs:
            logger.info(f"Found iframe with src: {iframe_tag['src']}")
            return iframe_tag['src']
        else:
            logger.warning("No src attribute found in the iframe tag.")
    else:
        logger.info("No iframe parameter provided.")
    return None

def process_url(url_data):
    url, note = url_data
    error_category = categorize_error(note)
    data_to_save = {'URL_Scrapped': url}
    
    try:
        if error_category in ['scraping_error', 'url_error']:
            wait_time = RETRY_WAIT_TIMES[error_category]
            retries = MAX_RETRIES[error_category]
            
            for attempt in range(retries):
                logger.info(f"Retry attempt {attempt + 1}/{retries} for {url}")
                
                soup = scrape_data(url, wait_time=wait_time)
                if not soup:
                    note = "Initial page scraping failed"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    continue
                
                unique_urls = get_unique_urls(soup, url)
                if not unique_urls:
                    note = "No unique URLs found"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    continue
                
                link = retrieve_room_link(unique_urls)
                if not link:
                    note = "Room link retrieval failed"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    continue
                
                data_to_save['URL_Scrapped'] = link
                note = "Room link retrieved successfully"
                logger.info(f"Successfully re-scraped {url} on attempt {attempt + 1}")
                save([{**data_to_save, 'Note': note}], 'success')
                return True
                
        elif error_category == 'data_error':
            wait_time = RETRY_WAIT_TIMES['data_error']
            retries = MAX_RETRIES['data_error']
            
            for attempt in range(retries):
                logger.info(f"Data retry attempt {attempt + 1}/{retries} for {url}")
                
                soup = scrape_data(url, wait_time)
                iframe_src = get_room_iframe_src(soup, True)
                if not iframe_src:
                    note = "Room page scraping failed"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    continue
                
                soup = scrape_data(iframe_src, wait_time)
                if not soup:
                    note = "Room page scraping failed"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    continue
                
                room_page_text = process_room_soup(soup)
                room_details = get_room_details(room_page_text)
                
                if not room_details:
                    note = "Room details retrieval failed"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    continue
                
                if isinstance(room_details, list):
                    for item in room_details:
                        if isinstance(item, tuple) and len(item) == 2:
                            key, value = item
                            data_to_save[key] = value
                        else:
                            logger.warning(f"Unexpected item in room_details: {item}")
                else:
                    note = "Room details in unexpected format"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    save([{**data_to_save, 'Note': note}], 'error')
                    continue
                
                note = "Room details retrieved successfully"
                processed_data = process(json.dumps(room_details), url)
                
                if not processed_data:
                    note = "Data processing failed"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    save([{**data_to_save, 'Note': note}], 'error')
                    continue
                
                note = "Data processed successfully"
                if save([{**item, 'Note': note} for item in processed_data], 'success'):
                    logger.info(f"Successfully processed data for {url} on attempt {attempt + 1}")
                    return True
                else:
                    note = "Processed data saving failed"
                    logger.error(f"{note} for {url} - attempt {attempt + 1}")
                    save([{**data_to_save, 'Note': note}], 'error')
                    continue
            
        elif error_category == 'save_error':
            note = "Processed data saving failed"
            logger.info(f"{note} for {url}")
            save([{**data_to_save, 'Note': note}], 'error')
            return False
            
        else:
            note = f"Unknown error category: {error_category}"
            logger.warning(f"{note} for {url}")
            save([{**data_to_save, 'Note': note}], 'error')
            return False
            
    except Exception as e:
        error_message = f"Error processing {url} (Note: {note}) on retry: {e}"
        logger.error(error_message)
        save([{**data_to_save, 'Note': error_message}], 'error')
        return False
    
    error_message = f"All retry failed"
    logger.error(error_message)
    save([{**data_to_save, 'Note': error_message}], 'error')
    return False

def retry_errors(error_csv_path, max_workers=DEFAULT_MAX_WORKERS):
    logger.info(f"Starting to retry errors from {error_csv_path}")
    
    errored_websites = read_error_csv(error_csv_path)
    logger.info(f"Found {len(errored_websites)} errored websites to retry")
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(process_url, url_data): url_data for url_data in errored_websites}
        for future in as_completed(future_to_url):
            url_data = future_to_url[future]
            try:
                success = future.result()
                results.append((url_data[0], url_data[1], success))
                logger.info(f"Completed retry for {url_data[0]}")
            except Exception as exc:
                error_message = f"Retry for {url_data[0]} generated an exception: {exc}"
                logger.error(error_message)
                save([{'URL_Scrapped': url_data[0], 'Note': error_message}], 'error')
                results.append((url_data[0], url_data[1], False))
    
    return results

def summarize_results(results):
    total = len(results)
    successful = sum(1 for _, _, success in results if success)
    logger.info(f"Retry summary: {successful}/{total} successfully processed")

def main_retry(error_csv_path):
    results = retry_errors(error_csv_path)
    summarize_results(results)

def get_latest_error_file():
    error_files = []
    for file in os.listdir('results'):
        if file.startswith('errors-') and file.endswith('.csv'):
            try:
                number = int(file.replace('errors-', '').replace('.csv', ''))
                error_files.append((number, file))
            except ValueError:
                continue
    
    if not error_files:
        return 'results/errors.csv'
    

    latest_file = max(error_files)[1]
    return os.path.join('results', latest_file)

if __name__ == "__main__":
    # error_csv_path = 'results/errors.csv'
    error_csv_path = get_latest_error_file()
    main_retry(error_csv_path)
