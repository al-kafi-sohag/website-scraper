import os
from groq import Groq
from dotenv import load_dotenv
from SimplerLLM.tools.json_helpers import extract_json_from_text
from logger_config import logger
from connect_ai import connect_to_ai

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Define a list of common endpoints
COMMON_ENDPOINTS = [
    "/all-rooms",
    "/rooms",
    "/find-rooms",
    "/room-list",
    "/hotel-rooms",
    "/homes-for-rent",
    "/rooms-for-rent",
    "/rental_listings",
    "/rental",
    "/search-results",
    "/available-rooms",
    "/accommodation",
    "/vacation-rentals",
    "/holiday-homes",
    "/property-listings",
    "/short-term-rentals",
    "/long-term-rentals",
    "/apartments-for-rent",
    "/rental-properties",
    "/stay",
    "/booking",
    "/reserve",
    "/book-now",
    "/lodging",
    "/find-accommodation",
    "/available-properties",
    "/housing",
    "/place-to-stay",
    "/stay-options",
    "/rentals",
    "/room-availability",
    "/bed-and-breakfast",
    "/bnb-listings",
    "/rental-units",
    "/residence",
    "/vacancy",
    "/hotels",
    "/find-hotels",
    "/hotel-listings",
    "/listing",
]


formatted_endpoints = ", ".join(f"`{endpoint}`" for endpoint in COMMON_ENDPOINTS)

prompt = f"""
You are an AI agent tasked with analyzing an array of URLs scraped from an online hotel listing website. Your job is to identify and return the URL that most accurately leads to a page listing all available hotels, houses, suites. 
The page should include room types, rates, and descriptions. Common endpoints for such pages might include URLs that contain phrases like {formatted_endpoints} or similar. 

Once you identify the most accurate URL, output it in the following JSON format:

{{
  "status": 1,
  "message": "Successfully retrieved the most accurate URL",
  "url": "URL_here"
}}

If no highly suitable URL is available, select the best possible match that most closely aligns with the criteria.

If an error occurs or if you are unable to process the request, return:

{{
  "status": -1,
  "message": add the error,
  "url": null
}}

Make sure to analyze the URLs carefully, prioritizing those that include terms indicating a room list page. Example terms include {formatted_endpoints} or similar.
Proceed with the analysis and provide the most accurate result.
Do not include any additional text, comments, or explanations outside of the JSON output. The response must strictly adhere to the JSON format as shown above.
"""


def extract_link(response):
    logger.info("Initiated extracting data")
    try:
        json_data = extract_json_from_text(response)
        if json_data:
            logger.info("Successfully extracted the data")
            data = json_data[0]
            status = data.get('status')
            message = data.get('message')
            url = data.get('url')
            
            match status:
              case 1:
                  logger.info(f"Success: {message}")
                  return url
              case 0:
                  logger.warning(f"No suitable URL: {message}")
                  return None
              case -1:
                  logger.error(f"Error: {message}")
                  return None
              case _:
                    logger.error(f"Unknown status: {status}")
                    return None
            
        else:
            logger.error("No data retrieved from AI")
    except Exception as e:
        logger.error(f"Error in extract_link: {e}")
        return None

def retrieve_room_link(urls):
    logger.info("Initiated Link retriever agent")
    response = connect_to_ai(prompt, f"Find the Room page url. From here:{urls}")
    if response:
        url = extract_link(response)
        logger.info(f"Processed all {len(urls)} urls")
        if url:
            logger.info(f"Total results retrieved: 1")
            logger.info(f"Retrieved URL: {url}")
            return url
        else:
            logger.warning("No valid URL extracted from AI response")
            return None
    else:
        logger.warning("No response from AI")
        return None
