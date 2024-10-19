import os
from groq import Groq
from dotenv import load_dotenv
from SimplerLLM.tools.json_helpers import extract_json_from_text


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = """
You are an AI agent tasked with analyzing an array of URLs scraped from an online hotel website. Your job is to identify and return the URL that leads to a page listing all available rooms at the hotel. 
The page should include room types, rates, and descriptions. Common endpoints for such pages might include URLs that contain phrases like `/all-rooms`, `/rooms`, `/find-rooms`, `/room-list`, `/hotel-rooms`, `/homes-for-rent`, or similar. 

Once you identify the correct URL, output it in the following JSON format:

{
  "status": 1,
  "message": "Successfully retrived the url"
  "url": "URL_here"
}

If no suitable URL is found, return:

{
  "status": 0,
  "message": "No Suitable URL"
  "url": null
}

If an error occurs or if you are unable to process the request, return:

{
  "status": -1,
  "message": add the error
  "url": null
}
Make sure to analyze the URLs carefully, and prioritize URLs that include terms indicating a room list page. 
Example terms include `/all-rooms`, `/find-rooms`, `/rooms`, or `/room-list`. 
Proceed with the analysis and provide the most accurate result.
Do not include any additional text, comments, or explanations outside of the JSON output. The response must strictly adhere to the JSON format as shown above.
"""

def connect_to_ai(urls):
  """
  Connects to the AI service and processes the given URLs to find the room link.
  Args:
  urls (list): A list of URLs to analyze.
  Returns:
  dict: A dictionary containing the status, message, and room_url (if found).
  """
  print(f"\n[INFO] Initiated Link retriever agent")
  try:
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Find the Room page url. From here:{urls}"}
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
  
def extract_link(response):
  print(f"\n[INFO] Initiated extracting data")
  try:
    json_data = extract_json_from_text(response)
    if json_data:
      print(f"[SUCCESS] Success fully extracted the data")
      data = json_data[0]
      status = data.get('status')
      message = data.get('message')
      url = data.get('url')
      
      match status:
        case 1:
          print(f"[INFO] {message}")
          return url
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

def retrieve_room_link(urls):
  response = connect_to_ai(urls)
  if response:
    url = extract_link(response)
    print(f"\n[INFO] Processed all {len(urls)} urls")
    print(f"[INFO] Total results retrieved: {len(url)}")
    print(f"{url}")
    return url
  else:
    return None

  

