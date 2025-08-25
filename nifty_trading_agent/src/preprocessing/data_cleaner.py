import pandas as pd
from ..utils.logger import logger

class DataCleaner:
    def __init__(self):
        logger.info("DataCleaner initialized.")

    def clean_market_data(self, df):
        logger.info("Cleaning market data...")
        # Handle missing values (e.g., forward fill, backward fill, or drop)
        df.fillna(method=\'ffill\', inplace=True)
        df.fillna(method=\'bfill\', inplace=True)

        # Remove duplicates
        df.drop_duplicates(inplace=True)

        # Convert data types if necessary
        for col in [\'open\', \'high\', \'low\', \'close\', \'volume\', \'oi\']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors=\'coerce\')
        
        # Remove rows with NaN values after conversion
        df.dropna(inplace=True)

        # Basic outlier detection (e.g., remove extreme values)
        # For example, remove rows where volume is 0 or negative
        if \'volume\' in df.columns:
            df = df[df[\'volume\'] > 0]

        logger.info("Market data cleaned.")
        return df

    def clean_sentiment_data(self, df):
        logger.info("Cleaning sentiment data...")
        df.dropna(subset=[\'text\', \'sentiment_score\'], inplace=True)
        df.drop_duplicates(subset=[\'text\', \'source\'], inplace=True)
        # Ensure sentiment_score is numeric
        df[\'sentiment_score\'] = pd.to_numeric(df[\'sentiment_score\'], errors=\'coerce\')
        df.dropna(subset=[\'sentiment_score\'], inplace=True)
        logger.info("Sentiment data cleaned.")
        return df




