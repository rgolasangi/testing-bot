import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from ..utils.logger import logger

class VolatilityAnalyzer:
    def __init__(self):
        logger.info("VolatilityAnalyzer initialized.")

    def calculate_historical_volatility(self, df, window=20, annualize=True):
        logger.info(f"Calculating historical volatility with window {window}...")
        if "close" not in df.columns:
            logger.warning("Close price column not found for volatility calculation.")
            return df

        df["Log_Return"] = np.log(df["close"] / df["close"].shift(1))
        daily_vol = df["Log_Return"].rolling(window=window).std()
        
        if annualize:
            df["Historical_Volatility"] = daily_vol * np.sqrt(252) # 252 trading days in a year
        else:
            df["Historical_Volatility"] = daily_vol
        logger.info("Historical volatility calculated.")
        return df

    def calculate_parkinson_volatility(self, df, window=20, annualize=True):
        logger.info(f"Calculating Parkinson volatility with window {window}...")
        if not all(col in df.columns for col in ["high", "low"]):
            logger.warning("High/Low price columns not found for Parkinson volatility.")
            return df

        df["Parkinson_Numerator"] = (np.log(df["high"]) - np.log(df["low"]))**2
        parkinson_vol = np.sqrt(df["Parkinson_Numerator"].rolling(window=window).mean() / (4 * np.log(2)))

        if annualize:
            df["Parkinson_Volatility"] = parkinson_vol * np.sqrt(252)
        else:
            df["Parkinson_Volatility"] = parkinson_vol
        logger.info("Parkinson volatility calculated.")
        return df

    def calculate_garman_klass_volatility(self, df, window=20, annualize=True):
        logger.info(f"Calculating Garman-Klass volatility with window {window}...")
        if not all(col in df.columns for col in ["open", "high", "low", "close"]):
            logger.warning("OHLC columns not found for Garman-Klass volatility.")
            return df

        log_hl = np.log(df["high"]) - np.log(df["low"])
        log_co = np.log(df["close"]) - np.log(df["open"])
        gk_vol = np.sqrt(0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2)
        garman_klass_vol = gk_vol.rolling(window=window).mean()

        if annualize:
            df["Garman_Klass_Volatility"] = garman_klass_vol * np.sqrt(252)
        else:
            df["Garman_Klass_Volatility"] = garman_klass_vol
        logger.info("Garman-Klass volatility calculated.")
        return df

    def calculate_volatility_cones(self, df, periods=[20, 60, 120, 252]):
        logger.info("Calculating volatility cones...")
        volatility_cones = pd.DataFrame(index=df.index)
        for p in periods:
            df_temp = self.calculate_historical_volatility(df.copy(), window=p, annualize=True)
            volatility_cones[f"Vol_{p}"] = df_temp["Historical_Volatility"]
        logger.info("Volatility cones calculated.")
        return volatility_cones

    def identify_volatility_regimes(self, df, n_clusters=3, feature_cols=None):
        logger.info(f"Identifying volatility regimes with {n_clusters} clusters...")
        if feature_cols is None:
            feature_cols = ["Historical_Volatility", "Parkinson_Volatility", "Garman_Klass_Volatility"]
        
        # Ensure volatility features are calculated
        df = self.calculate_historical_volatility(df.copy())
        df = self.calculate_parkinson_volatility(df.copy())
        df = self.calculate_garman_klass_volatility(df.copy())

        # Drop NaNs created by rolling windows
        df_clean = df.dropna(subset=feature_cols)

        if df_clean.empty:
            logger.warning("Not enough data to identify volatility regimes after dropping NaNs.")
            df["Volatility_Regime"] = np.nan
            return df

        X = df_clean[feature_cols].values
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10) # n_init added for KMeans
        df_clean["Volatility_Regime"] = kmeans.fit_predict(X)

        # Map regimes back to original DataFrame
        df = df.merge(df_clean[["Volatility_Regime"]], left_index=True, right_index=True, how="left")
        logger.info("Volatility regimes identified.")
        return df




