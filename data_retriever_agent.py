import os
import json
from groq import Groq
from dotenv import load_dotenv
from SimplerLLM.tools.json_helpers import extract_json_from_text

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
  print(f"\n[INFO] Initiated Data retriever agent")
  try:
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Extract the room data from here:{data}"}
    ]
    response = client.chat.completions.create(model=os.getenv("MODEL"), messages=messages)
    if response:
      print(f"[SUCCESS] Receieved response from AI")
      return response.choices[0].message.content
    else:
      print(f"[Warning] AI is returning empty response")
      return None
      
  except Exception as e:
    raise RuntimeError(f"[ERROR] {e}")
  
def extract_data(response):
  print(f"\n[INFO] Initiated extracting data")
  try:
    json_data = extract_json_from_text(response)
    if json_data:
      print(f"[SUCCESS] Success fully extracted the data")
      data = json_data[0]
      status = data.get('status')
      message = data.get('message')
      data = data.get('data')
      
      match status:
        case 1:
          print(f"[INFO] {message}")
          return data
        case 0:
          print(f"[WARNING] {message}")
          return None
        case -1:
          print(f"[Error] {message}")
          return None
        case _:
          print(f"[ERROR] Unknown status: {status}")
          return None
        
    else:
      print(f"[ERROR] No data retrieved from AI")
  except Exception as e:
    raise RuntimeError(f"[ERROR] {e}")

def chunk_data(data):
  print(f"\n[INFO] Initiated chunking data")
  try:
    words = data.split()
    chunks = []
    current_chunk = []
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= int(os.getenv("MAX_WORDS")):
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    print(f"[SUCCESS] Successfully chunked the data")
    print(f"[Info] Total chunk created: {len(chunks)}")
    return chunks
  except Exception as e:
    raise RuntimeError(f"[ERROR] {e}")

def retrieve_room_data(data):
  chunked_data = chunk_data(data)
  result = []

  for chunk in chunked_data:
    print(f"\n[INFO] Processing chunk {chunked_data.index(chunk) + 1} of {len(chunked_data)}")
    
    response = connect_to_ai(chunk)
    if response:
      chunk_result = extract_data(response)
      if chunk_result:
        result.extend(chunk_result)
    else:
      print(f"[WARNING] No response from AI for chunk {chunked_data.index(chunk) + 1}")
  
  print(f"\n[INFO] Processed all {len(chunked_data)} chunks")
  print(f"[INFO] Total results retrieved: {len(result)}")
  
  print("\nPretty-printed JSON result:")
  print(json.dumps(result, indent=2, ensure_ascii=False))

  return result
