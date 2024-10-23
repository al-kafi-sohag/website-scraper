import geocoder
from logger_config import logger
import os

def get_address_details(address):
    api_key = os.environ.get('OPENCAGE_API_KEY')
    
    if not api_key:
        logger.error("OpenCage API key not found in environment variables")
        return None

    try:
        logger.info(f"Attempting to geocode address: {address}")
        g = geocoder.opencage(address, key=api_key)
        
        if g.ok:
            logger.debug(f"Successfully geocoded address: {g}")
            
            # Extract the required components
            components = g.raw['components']
            street_number = components.get('house_number', '')
            street_name = components.get('road', '')
            zipcode = components.get('postcode', '')
            state = components.get('state', '')
            city = components.get('city', '') or components.get('town', '') or components.get('village', '')
            county = components.get('county', '')
            return {
                "Latitude": g.lat,
                "Longitude": g.lng,
                "Full_Address": g.address,
                "Street_Number": street_number,
                "Street_Name": street_name,
                "Zipcode": zipcode,
                "State": state,
                "City": city,
                "County": county
            }
        else:
            logger.warning(f"Could not find coordinates for address: {address}. Error: {g.error}")
            return None
    except Exception as e:
        logger.error(f"Error occurred while geocoding: {str(e)}")
        return None
