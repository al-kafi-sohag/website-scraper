import requests
import re
import json
from bs4 import BeautifulSoup
from link_retriever_agent import retrieve_room_link
from data_retriever_agent import retrieve_room_data


def scrape_data(url):
    print(f"\n[INFO] Initiated scrapper for link: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"[SUCCESS] Successfully scraped the data for link: {url}")
            return soup
        else:
            print(f"[ERROR] Failed to retrieve content. Status code: {response.status_code}")
            return None
    except Exception as e:
        raise RuntimeError(f"[ERROR] {e}")


def get_unique_urls(soup, base_url):
    print(f"\n[INFO] Initiated collecting urls")
    try:
        unique_urls = set()
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href'] 
            if not href.startswith(('http://', 'https://')):
                href = f"{base_url}{href}"
            if href.startswith(base_url):
                if href not in unique_urls:
                    unique_urls.add(href)
        
        print(f"[SUCCESS] Successfully collected all the urls")
        print(f"[INFO] Unique URL found: {len(unique_urls)}/{len(links)}")
        
        print("\nPretty-printed JSON result:")
        print(json.dumps(list(unique_urls), indent=2, ensure_ascii=False))
        
        return unique_urls
    except Exception as e:
        raise RuntimeError(f"[ERROR] {e}")
def get_room_details(text):
    print(f"\n[INFO] Initiated collecting room details")
    try:
        response = retrieve_room_data(text)
    except Exception as e:
        raise RuntimeError(f"[ERROR] {e}")
def process_room_soup(soup):
    for tag in soup(["head", "script", "style", "input", "textarea", "iframe", "noscript", "svg", "img", "br"]):
        tag.decompose()
        
    text = soup.get_text()
    
    # Remove extra whitespace and blank lines
    lines = (line.strip() for line in text.splitlines())
    text = '\n'.join(line for line in lines if line)
    
    # Remove any remaining HTML tags
    text = re.sub('<[^<]+?>', '', text)
    print(f"Text: {text}")
    return text

def main(base_url):
    soup = scrape_data(base_url)
    unique_urls = get_unique_urls(soup, base_url)
    link = retrieve_room_link(unique_urls)
    if link:
        room_page_soup = scrape_data(link)
        if room_page_soup:
            room_page_text = process_room_soup(room_page_soup)
            get_room_details(room_page_text)
    else:
        return None
    
if __name__ == "__main__":
    # main('https://www.roseviewhotel.com/')
    main('https://www.tonsofrentals.com')

