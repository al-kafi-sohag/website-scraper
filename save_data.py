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
        return

def generate_filepath(type):
    if type == 'success':
        return os.path.join('results', 'results.csv')
    else:
        # current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join('results', f'errors.csv')

def write_csv(filepath, data, mode='a'):
    try:
        fieldnames = ['URL_Scrapped', 'Website_Address', 'Full_Address', 'Street_Number', 'Street_Name', 'Zipcode', 
                      'State', 'City', 'County', 'Latitude', 'Longitude', 
                      'Beds', 'Bath', 'Price', 'Available', 'Note', 'Timestamp']
        
        file_exists = os.path.isfile(filepath)
        existing_data = []
        
        # Read existing data if file exists
        if file_exists:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                existing_data = list(reader)
        
        # Update existing data or add new entries
        updated_data = []
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for new_row in data:
            existing_row = next((row for row in existing_data if 
                                 row['URL_Scrapped'] == new_row.get('URL_Scrapped') and
                                 row['Website_Address'] == new_row.get('Website_Address')), None)
            if existing_row:
                existing_row.update(new_row)
                existing_row['Timestamp'] = current_timestamp
                existing_row['Note'] = 'Data updated successfully'
                updated_data.append(existing_row)
            else:
                new_row['Timestamp'] = current_timestamp
                updated_data.append(new_row)
        
        # Add remaining existing data that wasn't updated
        for row in existing_data:
            if row not in updated_data:
                updated_data.append(row)
        
        # Write updated data to file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in updated_data:
                row_data = {field: row.get(field, '') for field in fieldnames}
                writer.writerow(row_data)
        
        logger.info(f"Data successfully updated and saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save data to CSV: {e}")
        return

def save(data, type='success', mode='a'):
    try:
        if not data:
            logger.warning("No data to save")
            return False
        
        create_results_folder()
        filepath = generate_filepath(type)
        write_csv(filepath, data, mode)
        
        logger.info("Data saving completed successfully")
        return True
    except Exception as e:
        logger.error(f"An error occurred during data saving: {e}")
        return False
