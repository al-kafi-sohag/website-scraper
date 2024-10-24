import pandas as pd
import os
from logger_config import logger

def load_csv(file_path):
    if not os.path.exists(file_path):
        logger.error(f"CSV file not found: {file_path}")
        return 
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded CSV file with {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV file: {str(e)}")
        return 

def validate_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
        return 
    return True

def create_google_maps_link(lat, lon, add):
    if pd.notna(lat) and pd.notna(lon):
        return f"<a href='https://www.google.com/maps/search/?api=1&query={lat},{lon}' target='_blank'>{add}</a>"
    return ""

def add_link_column(df):
    df['link'] = df.apply(lambda row: create_google_maps_link(row['Latitude'], row['Longitude'], row['Full_Address']), axis=1)
    logger.info("Added 'link' column to the DataFrame")
    return df

def save_csv(df, file_path):
    try:
        df.to_csv(file_path, index=False)
        logger.info(f"Updated CSV saved to: {file_path}")
    except Exception as e:
        logger.error(f"Error saving CSV file: {str(e)}")

def main(file_path):
    df = load_csv(file_path)
    if df is None:
        logger.error("No data in the csv file")
        return

    required_columns = ['Latitude', 'Longitude', 'Full_Address']
    if not validate_columns(df, required_columns):
        return

    df = add_link_column(df)
    save_csv(df, file_path)
    logger.info("Google Maps links have been added to the CSV file.")

if __name__ == "__main__":
    file_path = 'results/results.csv'

    logger.info("Starting Google Maps link addition process")
    main(file_path)
    logger.info("Google Maps link addition process completed")
