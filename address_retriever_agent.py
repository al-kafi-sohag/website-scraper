import os
import geocoder
from groq import Groq
from dotenv import load_dotenv
from SimplerLLM.tools.json_helpers import extract_json_from_text
from logger_config import logger
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = """
You are an AI agent tasked with processing geocoding results. Your responsibilities include analyzing the provided geocoding data and extracting the most accurate and relevant information. Follow the steps below:

1. Carefully review the geocoding results.
2. Extract the most precise and complete address information.
3. If multiple results are present, select the most relevant one based on its alignment with the original query.
4. Structure the output in the specified JSON format:

{
  "status": 1,
  "message": "Successfully processed geocoding data",
  "data": {
    "formatted_address": "The most accurate full address",
    "latitude": "Latitude value",
    "longitude": "Longitude value",
    "street_number": "Street number if available",
    "street_name": "Street name",
    "city": "City name",
    "state": "State or province",
    "county": "County name",
    "postal_code": "Postal or ZIP code",
    "confidence": "Confidence score if available, otherwise use 'high' if the result is deemed accurate"
    
  }
}

5. If no suitable data is found, return the following response:

{
  "status": 0,
  "message": "No valid geocoding data found",
  "data": null
}

6. In case of any error during processing, output the following:

{
  "status": -1,
  "message": "Error processing geocoding data",
  "data": null
}

Make sure the JSON output strictly follows the given format without any extra comments or explanations outside the JSON structure.

"""

def connect_to_ai(geocoding_results):
    logger.info("Initiating AI connection for geocoding data processing")
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Process this geocoding data: {geocoding_results}"}
        ]
        response = client.chat.completions.create(model=os.getenv("MODEL"), messages=messages)
        if response and response.choices:
            logger.info("Successfully received AI response")
            logger.debug(f"Full AI response: {json.dumps(response.model_dump(), indent=2)}")
            logger.debug(f"AI response content: {response.choices[0].message.content}")
            return response.choices[0].message.content
        else:
            logger.warning("AI returned an empty or invalid response")
            return None
    except Exception as e:
        logger.error(f"Error during AI connection: {str(e)}")
        return None

def extract_geocoding_data(response):
    logger.info("Extracting data from AI response")
    if not response:
        logger.warning("No response to extract data from")
        return None
    
    try:
        json_data = extract_json_from_text(response)
        if not json_data:
            logger.error("Failed to extract JSON data from AI response")
            return None
        
        data = json_data[0]
        status = data.get('status')
        message = data.get('message')
        extracted_data = data.get('data')
        
        if status == 1:
            logger.info(f"Data extraction successful: {message}")
            return extracted_data
        elif status == 0:
            logger.warning(f"No data found: {message}")
        elif status == -1:
            logger.error(f"Error in data extraction: {message}")
        else:
            logger.error(f"Unknown status code: {status}")
        
        return None
    except Exception as e:
        logger.error(f"Error during data extraction: {str(e)}")
        return None

def process_geocoding_results(geocoding_results):
    if not geocoding_results:
        logger.warning("No geocoding results provided for processing")
        return None

    response = connect_to_ai(geocoding_results)

    if response:
        processed_data = extract_geocoding_data(response)
        if processed_data:
            logger.info("Successfully processed geocoding data")
            logger.debug(f"Processed data: {processed_data}")
            return processed_data
        else:
            logger.warning("Failed to extract data from AI response")
            return None
    else:
        logger.warning("Failed to connect to AI for geocoding data processing")
        return None

def get_address_details(address):
    api_key = os.environ.get('OPENCAGE_API_KEY')
    
    if not api_key:
        logger.error("OpenCage API key not found in environment variables")
        return None

    try:
        logger.info(f"Attempting to geocode address: {address}")
        g = geocoder.opencage(address, key=api_key, limit=5)  # Limit to 5 results, adjust as needed
        
        if g.ok:
            results = []
            results.append({'query_address': address})
            for result in g:
                results.append({
                    'formatted': result.address,
                    'lat': result.lat,
                    'lng': result.lng,
                    'confidence': result.confidence,
                    'components': result.raw['components'] if 'components' in result.raw else {}
                })
            logger.info(f"Found {len(results)} geocoding results")
            logger.debug(f"Geocoding result: {results}")
            return results
        else:
            logger.warning(f"Could not find coordinates for address: {address}. Error: {g.error}")
            return None
    except Exception as e:
        logger.error(f"Error occurred while geocoding: {str(e)}")
        return None

def retrieve_address(address):
    logger.info(f"Retrieving address details for: {address}")
    
    # Get geocoding results
    geocoding_results = get_address_details(address)
    
    if not geocoding_results:
        logger.warning("Failed to retrieve geocoding results")
        return None
    
    processed_data = process_geocoding_results(geocoding_results)
    
    if processed_data:
        logger.info("Successfully retrieved and processed address details")
        return processed_data
    else:
        logger.warning("Failed to process geocoding results")
        return None

def main():
    test_address = "1600 Amphitheatre Parkway, Mountain View, CA"
    logger.info(f"Testing address retrieval for: {test_address}")
    
    result = retrieve_address(test_address)
    
    if result:
        logger.info("Address retrieval successful")
        logger.info(f"Retrieved address details: {json.dumps(result, indent=2)}")
    else:
        logger.error("Address retrieval failed")

if __name__ == "__main__":
    main()
