from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ..utils.config_manager import config
from ..utils.logger import logger

class NewsCollector:
    def __init__(self):
        self.newsapi_client = NewsApiClient(api_key=config.get("news_api.api_key"))
        self.alpha_vantage_api_key = config.get("alphavantage.api_key")
        self.rss_feeds = {
            "Economic Times": "https://economictimes.indiatimes.com/rssfeeds/1221656.cms",
            "MoneyControl": "https://www.moneycontrol.com/rss/latestnews.xml",
            "NDTV Profit": "https://feeds.feedburner.com/NDTVProfit-Latest",
            "Business Standard": "https://www.business-standard.com/rss/home_page_rss.xml"
        }
        logger.info("NewsCollector initialized.")

    def get_newsapi_articles(self, query, from_param, to_param, language=\'en\'):
        try:
            articles = self.newsapi_client.get_everything(q=query, from_param=from_param, to_param=to_param, language=language, sort_by=\'relevancy\')
            logger.info(f"Fetched {len(articles.get(\'articles\', []))} articles from NewsAPI for query: {query}")
            return articles.get(\'articles\', [])
        except Exception as e:
            logger.error(f"Error fetching NewsAPI articles: {e}")
            return []

    def get_alpha_vantage_news(self, tickers=\'NIFTY\'):
        try:
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickers}&apikey={self.alpha_vantage_api_key}"
            r = requests.get(url)
            data = r.json()
            logger.info(f"Fetched {len(data.get(\'feed\', []))} articles from Alpha Vantage for tickers: {tickers}")
            return data.get(\'feed\', [])
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage news: {e}")
            return []

    def get_rss_feed_articles(self, feed_name, url):
        articles = []
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, \'xml\')
            items = soup.find_all(\'item\')
            for item in items:
                title = item.find(\'title\').text if item.find(\'title\') else \'No Title\'
                link = item.find(\'link\').text if item.find(\'link\') else \'No Link\'
                pub_date = item.find(\'pubDate\').text if item.find(\'pubDate\') else str(datetime.now())
                description = item.find(\'description\').text if item.find(\'description\') else \'No Description\'
                articles.append({
                    "source": feed_name,
                    "title": title,
                    "link": link,
                    "publishedAt": pub_date,
                    "description": description
                })
            logger.info(f"Fetched {len(articles)} articles from RSS feed: {feed_name}")
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_name}: {e}")
        return articles

    def collect_all_news(self, query=\'Nifty OR Bank Nifty\', days_ago=1):
        all_articles = []
        to_date = datetime.now().strftime(\'%Y-%m-%d\')
        from_date = (datetime.now() - timedelta(days=days_ago)).strftime(\'%Y-%m-%d\')

        # NewsAPI
        newsapi_arts = self.get_newsapi_articles(query, from_date, to_date)
        for art in newsapi_arts:
            all_articles.append({
                "source": art.get(\'source\', {}).get(\'name\', \'NewsAPI\'),
                "title": art.get(\'title\'),
                "description": art.get(\'description\'),
                "content": art.get(\'content\'),
                "publishedAt": art.get(\'publishedAt\'),
                "url": art.get(\'url\')
            })
        
        # Alpha Vantage News
        alpha_vantage_feed = self.get_alpha_vantage_news(tickers=\'NIFTY,BANKNIFTY\')
        for item in alpha_vantage_feed:
            all_articles.append({
                "source": item.get(\'source\'),
                "title": item.get(\'title\'),
                "description": item.get(\'summary\'),
                "content": item.get(\'content\'), # Alpha Vantage uses summary, not content
                "publishedAt": datetime.fromtimestamp(int(item.get(\'time_published\'))).isoformat(),
                "url": item.get(\'url\')
            })

        # RSS Feeds
        for feed_name, feed_url in self.rss_feeds.items():
            rss_arts = self.get_rss_feed_articles(feed_name, feed_url)
            for art in rss_arts:
                all_articles.append({
                    "source": art.get(\'source\'),
                    "title": art.get(\'title\'),
                    "description": art.get(\'description\'),
                    "content": art.get(\'description\'), # RSS often uses description as content
                    "publishedAt": art.get(\'publishedAt\'),
                    "url": art.get(\'link\')
                })
        
        # Deduplicate based on title and source
        unique_articles = {}
        for article in all_articles:
            key = (article.get(\'title\'), article.get(\'source\'))
            if key not in unique_articles:
                unique_articles[key] = article
        
        logger.info(f"Collected {len(unique_articles)} unique news articles.")
        return list(unique_articles.values())




