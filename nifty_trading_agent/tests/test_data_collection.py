import pytest
from unittest.mock import MagicMock, patch
from nifty_trading_agent.src.data_ingestion.data_collector import DataCollector
import pandas as pd
from datetime import datetime

@pytest.fixture
def data_collector():
    with patch("nifty_trading_agent.src.data_ingestion.data_collector.ZerodhaClient") as MockZerodhaClient,
         patch("nifty_trading_agent.src.data_ingestion.data_collector.db_manager") as MockDbManager:
        mock_zerodha_client = MockZerodhaClient.return_value
        mock_zerodha_client.get_historical_data.return_value = [
            {"date": "2023-01-01", "open": 100, "high": 110, "low": 90, "close": 105, "volume": 1000, "oi": 500},
            {"date": "2023-01-02", "open": 105, "high": 115, "low": 95, "close": 110, "volume": 1200, "oi": 600}
        ]
        mock_zerodha_client.get_quote.return_value = {
            123: {"last_price": 100, "tradingsymbol": "NIFTY", "ohlc": {"open": 99, "high": 101, "low": 98, "close": 100}, "volume": 500, "oi": 200}
        }
        mock_zerodha_client.get_instruments.return_value = [
            {"instrument_type": "CE", "tradingsymbol": "NIFTY24JAN19500CE"},
            {"instrument_type": "PE", "tradingsymbol": "NIFTY24JAN19500PE"},
            {"instrument_type": "EQ", "tradingsymbol": "RELIANCE"}
        ]
        yield DataCollector()

def test_collect_historical_data(data_collector):
    df = data_collector.collect_historical_data(123, "2023-01-01", "2023-01-02", "day")
    assert not df.empty
    assert len(df) == 2
    assert "instrument_token" in df.columns
    assert "timestamp" in df.columns
    data_collector.zerodha_client.get_historical_data.assert_called_once()
    data_collector.db_manager.add_market_data.call_count == 2

def test_collect_live_data(data_collector):
    data = data_collector.collect_live_data(123)
    assert data is not None
    assert data["instrument_token"] == 123
    assert data["close"] == 100
    data_collector.zerodha_client.get_quote.assert_called_once_with(123)
    data_collector.db_manager.add_market_data.assert_called_once()

def test_get_option_chain_data(data_collector):
    option_chain = data_collector.get_option_chain_data("NSE", "NIFTY")
    assert len(option_chain) == 2
    assert all("NIFTY" in opt["tradingsymbol"] for opt in option_chain)
    data_collector.zerodha_client.get_instruments.assert_called_once_with(exchange="NSE")


