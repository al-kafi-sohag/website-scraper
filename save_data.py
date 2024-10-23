import json
import csv
import os
from datetime import datetime
from logger_config import logger

def load_json_data(json_string):
    try:
        data = json.loads(json_string)
        logger.info(f"Successfully loaded JSON data with {len(data)} entries")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON data: {e}")
        return None

def create_results_folder():
    try:
        os.makedirs('results', exist_ok=True)
        logger.info("Results folder created or already exists")
    except Exception as e:
        logger.error(f"Failed to create results folder: {e}")
        raise

def generate_filepath(filename='results.csv'):
    return os.path.join('results', filename)

def write_csv(filepath, data, mode='a'):
    try:
        fieldnames = ['URL_Scrapped', 'Website_Address', 'Street_Number', 'Street_Name', 'Zipcode', 
                      'State', 'City', 'County', 'Timestamp', 'Latitude', 'Longitude', 
                      'Beds', 'Bath', 'Price', 'Available', 'Note']
        
        file_exists = os.path.isfile(filepath)
        
        with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists or mode == 'w':
                writer.writeheader()
            for row in data:
                row_data = {field: row.get(field, '') for field in fieldnames}
                writer.writerow(row_data)
        logger.info(f"Data successfully {'saved to' if mode == 'w' else 'appended to'} {filepath}")
    except Exception as e:
        logger.error(f"Failed to save data to CSV: {e}")
        raise

def save(data, mode='a'):
    try:
        if not data:
            logger.warning("No data to save")
            return False
        
        create_results_folder()
        filepath = generate_filepath()
        write_csv(filepath, data, mode)
        
        logger.info("Data saving completed successfully")
        return True
    except Exception as e:
        logger.error(f"An error occurred during data saving: {e}")
        return False
