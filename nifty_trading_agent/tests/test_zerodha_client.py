import pytest
from unittest.mock import MagicMock, patch
from nifty_trading_agent.src.data_ingestion.zerodha_client import ZerodhaClient
from kiteconnect import KiteConnect

@pytest.fixture
def zerodha_client():
    with patch("nifty_trading_agent.src.utils.config_manager.config") as mock_config:
        mock_config.get.side_effect = lambda key: {
            "zerodha.api_key": "test_api_key",
            "zerodha.api_secret": "test_api_secret",
            "zerodha.redirect_url": "http://localhost:3000/auth/zerodha"
        }.get(key)
        yield ZerodhaClient()

def test_zerodha_client_init(zerodha_client):
    assert zerodha_client.api_key == "test_api_key"
    assert zerodha_client.api_secret == "test_api_secret"
    assert zerodha_client.redirect_url == "http://localhost:3000/auth/zerodha"
    assert isinstance(zerodha_client.kite, KiteConnect)

def test_generate_session_success(zerodha_client):
    with patch.object(zerodha_client.kite, "generate_session") as mock_generate_session:
        mock_generate_session.return_value = {"access_token": "test_access_token"}
        result = zerodha_client.generate_session("test_request_token")
        assert result is True
        assert zerodha_client.access_token == "test_access_token"
        mock_generate_session.assert_called_once_with("test_request_token", api_secret="test_api_secret")

def test_generate_session_failure(zerodha_client):
    with patch.object(zerodha_client.kite, "generate_session") as mock_generate_session:
        mock_generate_session.side_effect = Exception("API Error")
        result = zerodha_client.generate_session("test_request_token")
        assert result is False
        assert zerodha_client.access_token is None

def test_set_access_token(zerodha_client):
    zerodha_client.set_access_token("new_access_token")
    assert zerodha_client.access_token == "new_access_token"

def test_get_login_url(zerodha_client):
    with patch.object(zerodha_client.kite, "login_url") as mock_login_url:
        mock_login_url.return_value = "http://login.url"
        url = zerodha_client.get_login_url()
        assert url == "http://login.url"

def test_get_historical_data(zerodha_client):
    with patch.object(zerodha_client.kite, "historical_data") as mock_historical_data:
        mock_historical_data.return_value = [{"date": "2023-01-01", "close": 100}]
        data = zerodha_client.get_historical_data(123, "2023-01-01", "2023-01-02", "day")
        assert data == [{"date": "2023-01-01", "close": 100}]

def test_place_order(zerodha_client):
    with patch.object(zerodha_client.kite, "place_order") as mock_place_order:
        mock_place_order.return_value = "order123"
        order_id = zerodha_client.place_order("regular", "NSE", "NIFTY", "BUY", 1, "MIS", "MARKET")
        assert order_id == "order123"

def test_get_positions(zerodha_client):
    with patch.object(zerodha_client.kite, "positions") as mock_positions:
        mock_positions.return_value = {"day": [], "overnight": []}
        positions = zerodha_client.get_positions()
        assert positions == {"day": [], "overnight": []}


