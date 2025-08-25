import pandas as pd
from scipy.stats import pearsonr
from ..utils.logger import logger

class CorrelationAnalyzer:
    def __init__(self):
        logger.info("CorrelationAnalyzer initialized.")

    def calculate_price_sentiment_correlation(self, market_data_df, sentiment_data_df, window=None, lag=0):
        logger.info(f"Calculating price-sentiment correlation with window {window} and lag {lag}...")
        if market_data_df.empty or sentiment_data_df.empty:
            logger.warning("Market data or sentiment data is empty. Cannot calculate correlation.")
            return None

        # Ensure timestamps are datetime objects and set as index
        market_data_df["timestamp"] = pd.to_datetime(market_data_df["timestamp"])
        sentiment_data_df["timestamp"] = pd.to_datetime(sentiment_data_df["timestamp"])
        
        market_data_df = market_data_df.set_index("timestamp").sort_index()
        sentiment_data_df = sentiment_data_df.set_index("timestamp").sort_index()

        # Resample sentiment data to match market data frequency (e.g., daily average sentiment)
        # This assumes market data is daily or can be resampled to match sentiment
        # For simplicity, let's resample sentiment to daily mean
        daily_sentiment = sentiment_data_df["sentiment_score"].resample("D").mean().fillna(method=\"ffill\")

        # Align dataframes based on common dates
        combined_df = market_data_df.join(daily_sentiment, how=\"inner\")

        if combined_df.empty:
            logger.warning("No overlapping dates between market and sentiment data. Cannot calculate correlation.")
            return None

        # Apply lag to sentiment data
        if lag > 0:
            combined_df["sentiment_score_lagged"] = combined_df["sentiment_score"].shift(lag)
            col_to_correlate = "sentiment_score_lagged"
        else:
            col_to_correlate = "sentiment_score"

        # Drop NaNs introduced by shifting or resampling
        combined_df = combined_df.dropna(subset=["close", col_to_correlate])

        if combined_df.empty:
            logger.warning("No data left after applying lag and dropping NaNs. Cannot calculate correlation.")
            return None

        if window:
            correlations = combined_df[col_to_correlate].rolling(window=window).corr(combined_df["close"])
        else:
            # Calculate single correlation for the entire period
            if len(combined_df) < 2:
                logger.warning("Not enough data points for correlation calculation.")
                return None
            correlation, _ = pearsonr(combined_df[col_to_correlate], combined_df["close"])
            correlations = pd.Series(correlation, index=[combined_df.index[-1]])

        logger.info("Price-sentiment correlation calculated.")
        return correlations

    def calculate_volatility_sentiment_correlation(self, volatility_df, sentiment_data_df, window=None, lag=0):
        logger.info(f"Calculating volatility-sentiment correlation with window {window} and lag {lag}...")
        if volatility_df.empty or sentiment_data_df.empty:
            logger.warning("Volatility data or sentiment data is empty. Cannot calculate correlation.")
            return None

        # Ensure timestamps are datetime objects and set as index
        volatility_df["timestamp"] = pd.to_datetime(volatility_df["timestamp"])
        sentiment_data_df["timestamp"] = pd.to_datetime(sentiment_data_df["timestamp"])

        volatility_df = volatility_df.set_index("timestamp").sort_index()
        sentiment_data_df = sentiment_data_df.set_index("timestamp").sort_index()

        # Resample sentiment data to match volatility data frequency (e.g., daily average sentiment)
        daily_sentiment = sentiment_data_df["sentiment_score"].resample("D").mean().fillna(method=\"ffill\")

        # Align dataframes based on common dates
        combined_df = volatility_df.join(daily_sentiment, how=\"inner\")

        if combined_df.empty:
            logger.warning("No overlapping dates between volatility and sentiment data. Cannot calculate correlation.")
            return None

        # Apply lag to sentiment data
        if lag > 0:
            combined_df["sentiment_score_lagged"] = combined_df["sentiment_score"].shift(lag)
            col_to_correlate = "sentiment_score_lagged"
        else:
            col_to_correlate = "sentiment_score"

        # Assuming volatility_df has a column named "Historical_Volatility" or similar
        vol_col = None
        for col in ["Historical_Volatility", "Parkinson_Volatility", "Garman_Klass_Volatility"]:
            if col in combined_df.columns:
                vol_col = col
                break
        
        if not vol_col:
            logger.error("No recognized volatility column found in volatility_df.")
            return None

        # Drop NaNs introduced by shifting or resampling
        combined_df = combined_df.dropna(subset=[vol_col, col_to_correlate])

        if combined_df.empty:
            logger.warning("No data left after applying lag and dropping NaNs. Cannot calculate correlation.")
            return None

        if window:
            correlations = combined_df[col_to_correlate].rolling(window=window).corr(combined_df[vol_col])
        else:
            # Calculate single correlation for the entire period
            if len(combined_df) < 2:
                logger.warning("Not enough data points for correlation calculation.")
                return None
            correlation, _ = pearsonr(combined_df[col_to_correlate], combined_df[vol_col])
            correlations = pd.Series(correlation, index=[combined_df.index[-1]])

        logger.info("Volatility-sentiment correlation calculated.")
        return correlations




