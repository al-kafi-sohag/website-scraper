import json
from datetime import datetime
from logger_config import logger
from address_retriever_agent import retrieve_address

def extract_fields(item):
    return (
        item.get('address'),
        item.get('beds'),
        item.get('bath'),
        item.get('price'),
        item.get('availability')
    )

def set_default_geolocation(item):
    fields = ['Street_Number', 'Street_Name', 'Zipcode', 'State', 'City', 
              'County', 'Latitude', 'Longitude']
    for field in fields:
        item[field] = None

def ensure_required_fields(item):
    required_fields = ['URL_Scrapped', 'Website_Address', 'Street_Number', 'Street_Name', 'Zipcode', 
                       'State', 'City', 'County', 'Timestamp', 'Latitude', 'Longitude', 
                       'Beds', 'Bath', 'Price', 'Available']
    for field in required_fields:
        if field not in item:
            item[field] = None

def process_item(item, url):
    try:
        address, beds, bath, price, available = extract_fields(item)

        processed_item = {
            'URL_Scrapped': url,
            'Beds': beds,
            'Bath': bath,
            'Price': price,
            'Available': available,
            'Website_Address': address,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        if address:
            # address_details = retrieve_address(address)
            address_details = None
            if address_details:
                if isinstance(address_details, list):
                    geolocation = address_details[0]
                else:
                    geolocation = address_details
                
                if geolocation:
                    processed_item.update({
                        'Street_Number': geolocation.get('street_number'),
                        'Street_Name': geolocation.get('street_name'),
                        'Zipcode': geolocation.get('postal_code'),
                        'State': geolocation.get('state'),
                        'City': geolocation.get('city'),
                        'County': geolocation.get('county'),
                        'Latitude': geolocation.get('latitude'),
                        'Longitude': geolocation.get('longitude')
                    })
                    logger.debug(f"Updated processed item with geolocation: {processed_item}")
                else:
                    logger.warning(f"Could not get geolocation for address: {address}")
                    set_default_geolocation(processed_item)
            else:
                logger.warning(f"Could not retrieve address details for: {address}")
                set_default_geolocation(processed_item)
        else:
            logger.warning("No address field found in the input data")
            set_default_geolocation(processed_item)

        ensure_required_fields(processed_item)
        return processed_item
    except Exception as e:
        logger.error(f"Error processing item: {str(e)}")
        return None

def process(data, url):
    logger.info("Starting data processing")
    
    try:
        data = json.loads(data) if isinstance(data, str) else data
        if not isinstance(data, list):
            logger.error("Input data is not a list")
            return None

        processed_data = [processed_item for item in data if (processed_item := process_item(item, url))]
        
        logger.info(f"Data processing completed successfully. Processed {len(processed_data)} items.")
        
        
        logger.debug("Retrieved process data: ")
        logger.debug(processed_data)
        return processed_data
    
    except Exception as e:
        logger.error(f"Error occurred during data processing: {str(e)}")
        return None

def main():
    test_data = [
        {
            "url": "https://example.com/property1",
            "address": "26 Edgemont Road, Asheville, NC 28801",
            "beds": 3,
            "bath": 2,
            "price": 350000,
            "availability": "Available"
        },
        {
            "url": "https://example.com/property2",
            "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
            "beds": 4,
            "bath": 3,
            "price": 1500000,
            "availability": "Sold"
        }
    ]

    logger.info("Starting test of process function")
    
    # Process the test data
    processed_data = process(test_data, "https://example.com")
    
    if processed_data:
        logger.info("Test completed successfully")
        logger.info(f"Processed {len(processed_data)} items")
        for item in processed_data:
            logger.debug(f"Processed item: {json.dumps(item, indent=2)}")
    else:
        logger.error("Test failed: process function returned None")

if __name__ == "__main__":
    main()
