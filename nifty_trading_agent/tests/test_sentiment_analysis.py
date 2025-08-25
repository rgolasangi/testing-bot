import pytest
from unittest.mock import MagicMock, patch
from nifty_trading_agent.src.sentiment_analysis.news_collector import NewsCollector
from nifty_trading_agent.src.sentiment_analysis.social_media_collector import SocialMediaCollector
from nifty_trading_agent.src.sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
import pandas as pd

@pytest.fixture
def news_collector():
    with patch("nifty_trading_agent.src.utils.config_manager.config") as mock_config:
        mock_config.get.side_effect = lambda key: {
            "news_api.api_key": "test_news_api_key",
            "alphavantage.api_key": "test_alpha_vantage_api_key"
        }.get(key)
        yield NewsCollector()

@pytest.fixture
def social_media_collector():
    with patch("nifty_trading_agent.src.utils.config_manager.config") as mock_config:
        mock_config.get.side_effect = lambda key: {
            "twitter.consumer_key": "ck", "twitter.consumer_secret": "cs",
            "twitter.access_token": "at", "twitter.access_token_secret": "ats",
            "reddit.client_id": "cid", "reddit.client_secret": "csc", "reddit.user_agent": "ua"
        }.get(key)
        yield SocialMediaCollector()

@pytest.fixture
def sentiment_analyzer():
    with patch("nifty_trading_agent.src.sentiment_analysis.sentiment_analyzer.pipeline") as mock_pipeline:
        mock_pipeline.return_value = MagicMock(return_value=[{"label": "neutral", "score": 0.9}])
        yield SentimentAnalyzer()

def test_news_collector_newsapi(news_collector):
    with patch.object(news_collector.newsapi_client, "get_everything") as mock_get_everything:
        mock_get_everything.return_value = {"articles": [{"title": "Test News", "source": {"name": "Test Source"}}]}
        articles = news_collector.get_newsapi_articles("test", "2023-01-01", "2023-01-02")
        assert len(articles) > 0
        assert articles[0]["title"] == "Test News"

def test_social_media_collector_tweets(social_media_collector):
    with patch("tweepy.OAuthHandler"), patch("tweepy.API") as MockAPI, patch("tweepy.Cursor") as MockCursor:
        mock_api_instance = MockAPI.return_value
        mock_tweet = MagicMock()
        mock_tweet.id_str = "123"
        mock_tweet.full_text = "This is a test tweet."
        mock_tweet.created_at = "2023-01-01"
        mock_tweet.user.screen_name = "testuser"
        mock_tweet.retweet_count = 10
        mock_tweet.favorite_count = 5
        MockCursor.return_value.items.return_value = [mock_tweet]
        
        tweets = social_media_collector.get_tweets("test")
        assert len(tweets) > 0
        assert tweets[0]["text"] == "This is a test tweet."

def test_sentiment_analyzer_overall_sentiment(sentiment_analyzer):
    text = "This is a great stock to buy!"
    sentiment = sentiment_analyzer.get_overall_sentiment(text)
    assert isinstance(sentiment, float)
    # Since FinBERT is mocked to return neutral, and VADER/TextBlob are real, this will be an average
    # We can't assert a specific value without knowing the exact VADER/TextBlob output, but it should be non-zero for positive text
    assert sentiment > -1.0 and sentiment < 1.0

def test_sentiment_analyzer_process_articles(sentiment_analyzer):
    articles_data = [
        {"title": "Good news", "description": "Market is up", "content": "", "source": "A"},
        {"title": "Bad news", "description": "Market is down", "content": "", "source": "B"}
    ]
    articles_df = pd.DataFrame(articles_data)
    processed_df = sentiment_analyzer.process_articles_for_sentiment(articles_df)
    assert "sentiment_score" in processed_df.columns
    assert "sentiment_magnitude" in processed_df.columns
    assert len(processed_df) == 2


