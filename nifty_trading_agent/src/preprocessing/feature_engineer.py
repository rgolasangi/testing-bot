import pandas as pd
import numpy as np
import talib
from ..utils.logger import logger

class FeatureEngineer:
    def __init__(self):
        logger.info("FeatureEngineer initialized.")

    def add_technical_indicators(self, df):
        logger.info("Adding technical indicators...")
        # Ensure columns are in correct format for TA-Lib
        if not all(col in df.columns for col in ["open", "high", "low", "close", "volume"]):
            logger.warning("Missing OHLCV data for technical indicator calculation.")
            return df

        # Moving Averages
        df["SMA_10"] = talib.SMA(df["close"], timeperiod=10)
        df["EMA_10"] = talib.EMA(df["close"], timeperiod=10)

        # RSI
        df["RSI"] = talib.RSI(df["close"], timeperiod=14)

        # MACD
        macd, macdsignal, macdhist = talib.MACD(df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
        df["MACD"] = macd
        df["MACD_Signal"] = macdsignal
        df["MACD_Hist"] = macdhist

        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(df["close"], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        df["BBL_Upper"] = upper
        df["BBL_Middle"] = middle
        df["BBL_Lower"] = lower

        # Stochastic Oscillator
        slowk, slowd = talib.STOCH(df["high"], df["low"], df["close"], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df["STOCH_K"] = slowk
        df["STOCH_D"] = slowd

        # ATR
        df["ATR"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=14)

        # ADX
        df["ADX"] = talib.ADX(df["high"], df["low"], df["close"], timeperiod=14)

        logger.info("Technical indicators added.")
        return df

    def add_volatility_features(self, df):
        logger.info("Adding volatility features...")
        if "close" not in df.columns:
            logger.warning("Missing close price for volatility calculation.")
            return df

        df["Log_Return"] = np.log(df["close"] / df["close"].shift(1))
        df["Daily_Volatility"] = df["Log_Return"].rolling(window=10).std() * np.sqrt(252) # Annualized
        logger.info("Volatility features added.")
        return df

    def add_options_features(self, df, option_chain_data=None):
        logger.info("Adding options features...")
        # This is a placeholder. Real options features would come from option chain data
        # and involve Greeks (Delta, Gamma, Theta, Vega, Rho), implied volatility, etc.
        # These would typically be calculated by the BlackScholesModel and integrated here.
        df["Option_Implied_Volatility"] = np.random.rand(len(df)) * 0.3 + 0.1 # Placeholder
        df["Option_Delta"] = np.random.rand(len(df)) * 2 - 1 # Placeholder (-1 to 1)
        df["Option_Theta"] = np.random.rand(len(df)) * -0.1 # Placeholder (negative)
        logger.info("Options features added.")
        return df

    def add_sentiment_features(self, df, sentiment_data=None):
        logger.info("Adding sentiment features...")
        # This is a placeholder. Real sentiment features would be merged based on timestamp
        # from the sentiment analysis module.
        df["Sentiment_Score"] = np.random.rand(len(df)) * 2 - 1 # Placeholder (-1 to 1)
        df["Sentiment_Magnitude"] = np.random.rand(len(df)) # Placeholder (0 to 1)
        logger.info("Sentiment features added.")
        return df

    def create_rl_state_space(self, df):
        logger.info("Creating RL state space...")
        # Select and normalize features for the RL agent
        features = [
            "open", "high", "low", "close", "volume", "oi",
            "SMA_10", "EMA_10", "RSI", "MACD", "MACD_Signal", "MACD_Hist",
            "BBL_Upper", "BBL_Middle", "BBL_Lower", "STOCH_K", "STOCH_D",
            "ATR", "ADX", "Log_Return", "Daily_Volatility",
            "Option_Implied_Volatility", "Option_Delta", "Option_Theta",
            "Sentiment_Score", "Sentiment_Magnitude"
        ]
        
        # Ensure all features exist, fill NaNs if necessary (e.g., after TA-Lib calculations)
        for feature in features:
            if feature not in df.columns:
                df[feature] = 0 # Or a more sophisticated imputation
        df = df.fillna(0) # Final NaN fill

        state_space_df = df[features]
        # Normalize features (Min-Max scaling or StandardScaler)
        # For simplicity, a basic normalization:
        state_space_df = (state_space_df - state_space_df.mean()) / state_space_df.std()
        state_space_df = state_space_df.fillna(0) # Handle cases where std is 0

        logger.info(f"RL state space created with {len(features)} features.")
        return state_space_df




