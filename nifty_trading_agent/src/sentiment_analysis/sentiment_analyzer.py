from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline
import pandas as pd
from ..utils.logger import logger

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        # Initialize FinBERT (or similar pre-trained model for financial sentiment)
        # This requires downloading the model, which can be large.
        # Ensure you have internet access and sufficient memory.
        try:
            self.finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            logger.info("FinBERT model loaded successfully.")
        except Exception as e:
            self.finbert = None
            logger.warning(f"Could not load FinBERT model: {e}. Financial sentiment analysis will be limited.")
        logger.info("SentimentAnalyzer initialized.")

    def analyze_vader(self, text):
        return self.vader.polarity_scores(text)["compound"]

    def analyze_textblob(self, text):
        return TextBlob(text).sentiment.polarity

    def analyze_finbert(self, text):
        if not self.finbert:
            return 0.0 # Return neutral if FinBERT not loaded
        try:
            result = self.finbert(text)
            if result and len(result) > 0:
                label = result[0]["label"]
                score = result[0]["score"]
                if label == "positive":
                    return score
                elif label == "negative":
                    return -score
                else:
                    return 0.0 # Neutral
            return 0.0
        except Exception as e:
            logger.error(f"Error analyzing with FinBERT: {e}")
            return 0.0

    def get_overall_sentiment(self, text):
        vader_score = self.analyze_vader(text)
        textblob_score = self.analyze_textblob(text)
        finbert_score = self.analyze_finbert(text)

        # Simple aggregation: average the scores. Could be weighted.
        scores = [vader_score, textblob_score]
        if self.finbert:
            scores.append(finbert_score)
        
        overall_score = sum(scores) / len(scores)
        return overall_score

    def analyze_batch(self, texts):
        results = []
        for text in texts:
            results.append(self.get_overall_sentiment(text))
        return results

    def process_articles_for_sentiment(self, articles_df):
        logger.info("Processing articles for sentiment analysis...")
        if articles_df.empty:
            logger.warning("No articles to process for sentiment.")
            return pd.DataFrame()

        articles_df["full_text"] = articles_df["title"].fillna("") + " " + \
                                  articles_df["description"].fillna("") + " " + \
                                  articles_df["content"].fillna("")
        articles_df["full_text"] = articles_df["full_text"].apply(lambda x: x.strip())

        # Apply sentiment analysis
        articles_df["sentiment_score"] = articles_df["full_text"].apply(self.get_overall_sentiment)
        
        # For simplicity, magnitude can be absolute of score or a separate calculation
        articles_df["sentiment_magnitude"] = articles_df["sentiment_score"].apply(abs)

        logger.info("Sentiment analysis completed for articles.")
        return articles_df




