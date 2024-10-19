import os
import json
from groq import Groq
from dotenv import load_dotenv
from SimplerLLM.tools.json_helpers import extract_json_from_text
from logger_config import logger

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = """

You are a data retrieval agent tasked with processing scraped data from a hotel booking website. Your job is to extract details: room name, location and price information into a structured JSON format.

Once you identify the data, output it in the following JSON format:

{
  "status": 1,
  "message": "Successfully retrived the data",
  "data": [
      {
          "name": "name of the room"
          "address": "address of the room",
          "price": "price with currency if avaiable"
      },
      {
          "name": "name of another room"
          "address": "address of another room",
          "price": "price with currency if avaiable"
      }
  ]
}

If no suitable data is found, return:

{
  "status": 0,
  "message": "No data found",
  "data": None
}

If an error occurs or if you are unable to process the request, return:

{
  "status": -1,
  "message": "add the error",
  "data": None
}

1. Only include hotels and rooms where the name, location and price are specified. 
2. Ensure accuracy and completeness when listing room types and pricing options.
3. Proceed with the analysis and provide the most accurate result.
4. Do not include any additional text, comments, or explanations outside of the JSON output. The response must strictly adhere to the JSON format as shown above.
"""

def connect_to_ai(data):
    logger.info("Initiating AI connection for data retrieval")
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Extract the room data from here: {data}"}
        ]
        response = client.chat.completions.create(model=os.getenv("MODEL"), messages=messages)
        if response and response.choices:
            logger.info("Successfully received AI response")
            return response.choices[0].message.content
        else:
            logger.warning("AI returned an empty or invalid response")
            return None
    except Exception as e:
        logger.error(f"Error during AI connection: {str(e)}")
        return None

def extract_data(response):
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

def chunk_data(data):
    logger.info("Initiating data chunking process")
    if not data:
        logger.warning("No data to chunk")
        return []
    
    try:
        words = data.split()
        max_words = int(os.getenv("MAX_WORDS", 1000))  # Default to 1000 if not set
        chunks = [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]
        
        logger.info(f"Data chunking completed. Total chunks created: {len(chunks)}")
        return chunks
    except Exception as e:
        logger.error(f"Error during data chunking: {str(e)}")
        return []

def retrieve_room_data(data):
    if not data:
        logger.warning("No data provided for room retrieval")
        return []

    chunked_data = chunk_data(data)
    result = []

    for index, chunk in enumerate(chunked_data, 1):
        logger.info(f"Processing chunk {index} of {len(chunked_data)}")
        
        response = connect_to_ai(chunk)
        if response:
            chunk_result = extract_data(response)
            if chunk_result:
                result.extend(chunk_result)
        else:
            logger.warning(f"No AI response for chunk {index}")
    
    logger.info(f"Room data retrieval completed. Total results: {len(result)}")
    
    if result:
        logger.debug("Retrieved room data (first 3 entries):")
        logger.debug(json.dumps(result[:3], indent=2, ensure_ascii=False))
    else:
        logger.warning("No room data retrieved")

    return result
