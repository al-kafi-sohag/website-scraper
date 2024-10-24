import geocoder
from logger_config import logger
import os

def geocode_with_opencage(address, api_key):
    try:
        logger.info(f"Attempting to geocode address with OpenCage: {address}")
        g = geocoder.opencage(address, key=api_key)
        
        if g.ok:
            logger.debug(f"Successfully geocoded address with OpenCage: {g}")
            components = g.raw['components']
            return {
                "Latitude": g.lat,
                "Longitude": g.lng,
                "Full_Address": g.address,
                "Street_Number": components.get('house_number', ''),
                "Street_Name": components.get('road', ''),
                "Zipcode": components.get('postcode', ''),
                "State": components.get('state', ''),
                "City": components.get('city', '') or components.get('town', '') or components.get('village', ''),
                "County": components.get('county', '')
            }
        else:
            logger.warning(f"OpenCage could not find coordinates for address: {address}. Error: {g.error}")
            return None
    except Exception as e:
        logger.error(f"Error occurred while geocoding with OpenCage: {str(e)}")
        return None

def geocode_with_google(address, api_key):
    try:
        logger.info(f"Attempting to geocode address with Google: {address}")
        g = geocoder.google(address, key=api_key)
        
        if g.ok:
            logger.debug(f"Successfully geocoded address with Google: {g}")
            components = g.json['raw']['address_components']
            return {
                "Latitude": g.lat,
                "Longitude": g.lng,
                "Full_Address": g.address,
                "Street_Number": next((item['long_name'] for item in components if 'street_number' in item['types']), ''),
                "Street_Name": next((item['long_name'] for item in components if 'route' in item['types']), ''),
                "Zipcode": next((item['long_name'] for item in components if 'postal_code' in item['types']), ''),
                "State": next((item['long_name'] for item in components if 'administrative_area_level_1' in item['types']), ''),
                "City": next((item['long_name'] for item in components if 'locality' in item['types']), ''),
                "County": next((item['long_name'] for item in components if 'administrative_area_level_2' in item['types']), '')
            }
        else:
            logger.warning(f"Google could not find coordinates for address: {address}. Error: {g.error}")
            return None
    except Exception as e:
        logger.error(f"Error occurred while geocoding with Google: {str(e)}")
        return None

def get_address_details(address):
    # Get API keys from environment variables
    opencage_api_key = os.environ.get('OPENCAGE_API_KEY')
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    geocoding_service = os.environ.get('GEOCODING_SERVICE', 'opencage').lower()

    if geocoding_service not in ['opencage', 'google']:
        logger.error("Invalid geocoding service specified. Use 'opencage' or 'google'.")
        return None

    if geocoding_service == 'opencage' and opencage_api_key:
        result = geocode_with_opencage(address, opencage_api_key)
        if result:
            return result

    if geocoding_service == 'google' and google_api_key:
        result = geocode_with_google(address, google_api_key)
        if result:
            return result

    logger.error("Failed to retrieve address details using the specified service")
    return None
