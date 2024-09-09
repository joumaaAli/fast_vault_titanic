import hashlib
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class Hasher:
    def anonymize_data(self, data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        logger.info(f"Anonymizing data for columns: {columns}")
        try:
            for column in columns:
                if column in data.columns:
                    data[column] = data[column].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest())
            logger.info("Data anonymization completed successfully.")
            return data
        except Exception as e:
            logger.error(f"Error during data anonymization: {e}")
            raise
