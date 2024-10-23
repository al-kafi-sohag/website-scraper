import json
import csv
import os
from datetime import datetime
from logger_config import logger
from geolocation import get_geolocation
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

def save_to_csv(data, filename_prefix='Result'):
    timestamp = datetime.now().strftime("%Y-%m-%d %H %M %S")
    filename = f"{filename_prefix}-{timestamp}.csv"
    filepath = os.path.join('results', filename)
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['address', 'price', 'availability']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        logger.info(f"Data successfully saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save data to CSV: {e}")
        raise

def process_and_save_data(json_string):
    try:
        data = load_json_data(json_string)
        if not data:
            return None
        
        create_results_folder()
        
        save_to_csv(data)
        # save_to_drive(data)
        
        logger.info("Data processing and saving completed successfully")
        
        return True
    except Exception as e:
        logger.error(f"An error occurred during data processing: {e}")

def save_to_drive(data):
    try:
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'])
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)

        folder_name = 'Property Data Results'
        folder_id = get_or_create_folder(drive_service, folder_name)

        sheet = create_sheet(drive_service, sheets_service, folder_id, data)

        logger.info(f"Data successfully saved to Google Drive in folder '{folder_name}' with Sheet ID: {sheet['id']}")
        return sheet['id']
    except HttpError as error:
        logger.error(f"An error occurred while saving to Google Drive: {error}")
        raise

def get_or_create_folder(service, folder_name):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    folders = results.get('files', [])

    if not folders:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    
    return folders[0]['id']

def create_sheet(drive_service, sheets_service, folder_id, data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet_metadata = {
        'name': f'Property Data - {timestamp}',
        'parents': [folder_id],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    sheet = drive_service.files().create(body=sheet_metadata, fields='id').execute()
    sheet_id = sheet.get('id')

    # Prepare the data for the sheet
    values = [['address', 'price', 'availability']]
    values.extend([[row['address'], row['price'], row['availability']] for row in data])

    body = {
        'values': values
    }
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range='A1', valueInputOption='RAW', body=body).execute()

    return sheet
