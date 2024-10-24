import pandas as pd
import os
from geolocation import get_address_details
from logger_config import logger

def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded CSV file with {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV file: {str(e)}")
        return None

def save_csv(file_path, df):
    try:
        df.to_csv(file_path, index=False)
        logger.info(f"Updated CSV saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving CSV file: {str(e)}")

def filter_rows_to_process(df, max_rows):
    rows_to_process = df[df[['Latitude', 'Longitude']].isna().all(axis=1)]
    logger.info(f"Rows with empty Latitude and Longitude: {len(rows_to_process)}")
    
    rows_to_process = rows_to_process.head(max_rows)
    logger.info(f"Filtered to {len(rows_to_process)} rows (max_rows: {max_rows})")
    
    return rows_to_process

def process_row(row):
    allowed_columns = ['Full_Address', 'Street_Number', 'Street_Name', 'Zipcode',
                       'State', 'City', 'County', 'Latitude', 'Longitude']
    
    if pd.isna(row['Latitude']) and pd.isna(row['Longitude']):
        address = row['Website_Address']
        if pd.notna(address):
            details = get_address_details(address)
            if details:
                filtered_details = {k: v if v is not None else '' for k, v in details.items() if k in allowed_columns}
                if any(filtered_details.values()):
                    row.update(filtered_details)
                else:
                    logger.warning(f"No valid details found for address: {address}")
            else:
                logger.warning(f"No details returned for address: {address}")
        else:
            logger.warning(f"Skipping row with empty Website_Address")
    return row

def process_data(file_path, max_rows):
    df = load_csv(file_path)
    if df is None:
        return

    rows_to_process = filter_rows_to_process(df, max_rows)
    processed_df = rows_to_process.apply(process_row, axis=1)

    df.update(processed_df)
    save_csv(file_path, df)

if __name__ == "__main__":
    file_path = "results/results.csv"
    max_rows = int(os.getenv('MAX_ADDRESS_ROWS', 100))

    logger.info("Starting address processing")
    process_data(file_path, max_rows)
    logger.info("Address processing completed")
