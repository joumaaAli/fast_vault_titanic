import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Replace the database fetch function with a function to read from CSV
def get_all_data_records_from_csv(csv_path: str) -> pd.DataFrame:
    try:
        data = pd.read_csv(csv_path)
        return data
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {e}")
        raise ValueError("CSV file not found.")
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise ValueError("Error reading CSV file.")

def convert_data_records_to_dataframe(records):
    return pd.DataFrame([record.dict() for record in records])
