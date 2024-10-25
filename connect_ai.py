import os
import time
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
from logger_config import logger

load_dotenv()

GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def connect_to_groq(prompt, user_content):
    logger.info("Initiating Groq AI connection")
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
        response = GROQ_CLIENT.chat.completions.create(model=os.getenv("GROQ_MODEL"), messages=messages)
        if response and response.choices:
            logger.info("Successfully received Groq AI response")
            logger.debug(f"Response: {response.choices[0].message.content[:100]}...")
            return response.choices[0].message.content
        else:
            logger.warning("Groq AI returned an empty or invalid response")
            return None
    except Exception as e:
        logger.error(f"Error during Groq AI connection: {str(e)}")
        return None

def connect_to_gemini(prompt, user_content):
    logger.info("Initiating Gemini AI connection")
    try:
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
        response = model.generate_content([prompt, user_content])
        if response and response.text:
            logger.info("Successfully received Gemini AI response")
            logger.debug(f"Response: {response.text[:100]}...")
            return response.text
        else:
            logger.warning("Gemini AI returned an empty or invalid response")
            return None
    except Exception as e:
        logger.error(f"Error during Gemini AI connection: {str(e)}")
        return None

def connect_to_ai(prompt, user_content):
    logger.info("Initiating AI connection")
    time.sleep(5)
    ai_provider = os.getenv("AI_PROVIDER", "groq").lower()
    
    if ai_provider == "groq":
        return connect_to_groq(prompt, user_content)
    elif ai_provider == "gemini":
        return connect_to_gemini(prompt, user_content)
    else:
        logger.error(f"Unknown AI provider: {ai_provider}")
        return None
