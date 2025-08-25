import tweepy
import praw
from datetime import datetime, timedelta
from ..utils.config_manager import config
from ..utils.logger import logger

class SocialMediaCollector:
    def __init__(self):
        # Twitter API (X API)
        self.twitter_client = self._init_twitter_client()

        # Reddit API
        self.reddit_client = self._init_reddit_client()
        logger.info("SocialMediaCollector initialized.")

    def _init_twitter_client(self):
        try:
            consumer_key = config.get("twitter.consumer_key")
            consumer_secret = config.get("twitter.consumer_secret")
            access_token = config.get("twitter.access_token")
            access_token_secret = config.get("twitter.access_token_secret")

            if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                logger.warning("Twitter API credentials not fully configured. Skipping Twitter client initialization.")
                return None

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            return tweepy.API(auth)
        except Exception as e:
            logger.error(f"Error initializing Twitter client: {e}")
            return None

    def _init_reddit_client(self):
        try:
            client_id = config.get("reddit.client_id")
            client_secret = config.get("reddit.client_secret")
            user_agent = config.get("reddit.user_agent")

            if not all([client_id, client_secret, user_agent]):
                logger.warning("Reddit API credentials not fully configured. Skipping Reddit client initialization.")
                return None

            return praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {e}")
            return None

    def get_tweets(self, query, count=100):
        tweets_data = []
        if not self.twitter_client:
            logger.warning("Twitter client not initialized. Cannot fetch tweets.")
            return tweets_data
        try:
            for tweet in tweepy.Cursor(self.twitter_client.search_tweets, q=query, lang="en", tweet_mode=\"extended\").items(count):
                tweets_data.append({
                    "source": "Twitter",
                    "id": tweet.id_str,
                    "text": tweet.full_text,
                    "created_at": tweet.created_at,
                    "user": tweet.user.screen_name,
                    "retweet_count": tweet.retweet_count,
                    "favorite_count": tweet.favorite_count
                })
            logger.info(f"Fetched {len(tweets_data)} tweets for query: {query}")
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
        return tweets_data

    def get_reddit_posts(self, subreddit_name, query, limit=100):
        reddit_data = []
        if not self.reddit_client:
            logger.warning("Reddit client not initialized. Cannot fetch Reddit posts.")
            return reddit_data
        try:
            subreddit = self.reddit_client.subreddit(subreddit_name)
            for submission in subreddit.search(query, limit=limit):
                reddit_data.append({
                    "source": "Reddit",
                    "id": submission.id,
                    "title": submission.title,
                    "text": submission.selftext,
                    "created_at": datetime.fromtimestamp(submission.created_utc),
                    "author": submission.author.name if submission.author else "[deleted]",
                    "score": submission.score,
                    "num_comments": submission.num_comments
                })
            logger.info(f"Fetched {len(reddit_data)} Reddit posts from r/{subreddit_name} for query: {query}")
        except Exception as e:
            logger.error(f"Error fetching Reddit posts: {e}")
        return reddit_data

    def collect_all_social_media(self, query=\"Nifty OR Bank Nifty\"):
        all_posts = []
        
        # Collect Tweets
        all_posts.extend(self.get_tweets(query))

        # Collect Reddit posts from relevant subreddits
        all_posts.extend(self.get_reddit_posts("indiainvestments", query))
        all_posts.extend(self.get_reddit_posts("IndianStockMarket", query))
        all_posts.extend(self.get_reddit_posts("StockMarket", query))

        logger.info(f"Collected a total of {len(all_posts)} social media posts.")
        return all_posts




