import os
import json
from groq import Groq
from dotenv import load_dotenv
from SimplerLLM.tools.json_helpers import extract_json_from_text
from logger_config import logger

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = """

You are a data extraction agent tasked with processing data from a hotel booking website. Your job is to identify and extract the details of the house  address, price and availablity into a structured JSON format. Adhere strictly to the following instructions:

1. Extract only data where the room name, location, and price are clearly mentioned. If any of these details are missing, exclude that entry.

2. Structure your output in the JSON format below, ensuring consistency and completeness:

{
  "status": 1,
  "message": "Successfully retrieved the data",
  "data": [
    {
      "address": "address of the room if data is present, else keep it empty",
      "price": "price with currency if data is present, else keep it empty",
      "availability": "availability status if present, else keep it empty"
    },
    {
      "address": "another address of the room if data is present, else keep it empty",
      "price": "another price with currency if data is present, else keep it empty",
      "availability": "another availability status if present, else keep it empty"
    }
  ]
}

3. If no suitable data is identified, return the following:

{
  "status": 0,
  "message": "No data found",
  "data": null
}

4. If an error occurs during processing, or you are unable to fulfill the request, return the following:

{
  "status": -1,
  "message": "Include a brief description of the error",
  "data": null
}

5. Ensure that the output strictly adheres to the JSON format, without any additional explanations or comments outside of the JSON response.

6. Proceed with the extraction task and provide the most accurate and complete result possible.

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
            logger.debug(f"Response: {response.choices[0].message.content[:100]}...")
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
        logger.debug("Retrieved room data:")
        logger.debug(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        logger.warning("No room data retrieved")

    return result
