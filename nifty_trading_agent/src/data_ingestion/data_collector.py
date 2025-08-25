import pandas as pd
from datetime import datetime, timedelta
from ..data_ingestion.zerodha_client import ZerodhaClient
from ..utils.database import db_manager
from ..utils.logger import logger

class DataCollector:
    def __init__(self):
        self.zerodha_client = ZerodhaClient()

    def collect_historical_data(self, instrument_token, from_date, to_date, interval):
        logger.info(f"Collecting historical data for {instrument_token} from {from_date} to {to_date} with interval {interval}")
        data = self.zerodha_client.get_historical_data(instrument_token, from_date, to_date, interval)
        if data:
            df = pd.DataFrame(data)
            df["instrument_token"] = instrument_token
            df["tradingsymbol"] = "NIFTY_50" # Placeholder, ideally map token to symbol
            df["timestamp"] = df["date"].apply(lambda x: x.to_pydatetime() if isinstance(x, pd.Timestamp) else x)
            df = df.rename(columns={"open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume", "oi": "oi"})
            df = df[["instrument_token", "tradingsymbol", "timestamp", "open", "high", "low", "close", "volume", "oi"]]
            
            # Store in database
            for index, row in df.iterrows():
                db_manager.add_market_data(row.to_dict())
            logger.info(f"Successfully collected and stored {len(df)} historical data points.")
            return df
        logger.warning(f"No historical data collected for {instrument_token}.")
        return pd.DataFrame()

    def collect_live_data(self, instrument_token):
        logger.info(f"Collecting live data for {instrument_token}")
        quote = self.zerodha_client.get_quote(instrument_token)
        if quote and instrument_token in quote:
            data = quote[instrument_token]["last_price"]
            # In a real scenario, you'd get more details like OHLC, volume, OI
            # For simplicity, let's assume we get a full candle or tick data
            live_data = {
                "instrument_token": instrument_token,
                "tradingsymbol": quote[instrument_token]["tradingsymbol"], # Use actual tradingsymbol
                "timestamp": datetime.now(),
                "open": quote[instrument_token].get("ohlc", {}).get("open", data),
                "high": quote[instrument_token].get("ohlc", {}).get("high", data),
                "low": quote[instrument_token].get("ohlc", {}).get("low", data),
                "close": data,
                "volume": quote[instrument_token].get("volume", 0),
                "oi": quote[instrument_token].get("oi", 0)
            }
            db_manager.add_market_data(live_data)
            logger.info(f"Collected live data for {instrument_token}: {data}")
            return live_data
        logger.warning(f"No live data collected for {instrument_token}.")
        return None

    def get_option_chain_data(self, exchange, tradingsymbol):
        logger.info(f"Fetching option chain for {tradingsymbol} on {exchange}")
        # Zerodha KiteConnect does not provide a direct option chain API.
        # This function would need to be implemented by:
        # 1. Fetching all instruments for the exchange.
        # 2. Filtering for options related to the tradingsymbol (e.g., NIFTY, BANKNIFTY).
        # 3. Parsing strike prices, expiry dates, and option types (CE/PE).
        # 4. For live Greeks, you'd need to fetch quotes for each option instrument.
        
        # Placeholder implementation:
        instruments = self.zerodha_client.get_instruments(exchange=exchange)
        option_chain = []
        if instruments:
            for inst in instruments:
                if inst["instrument_type"] == "CE" or inst["instrument_type"] == "PE":
                    if tradingsymbol.upper() in inst["tradingsymbol"].upper():
                        option_chain.append(inst)
        logger.info(f"Found {len(option_chain)} options for {tradingsymbol}.")
        return option_chain




