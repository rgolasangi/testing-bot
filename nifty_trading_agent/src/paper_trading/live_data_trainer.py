import time
from datetime import datetime, timedelta
import pandas as pd
import os

from nifty_trading_agent.src.data_ingestion.zerodha_client import ZerodhaClient
from nifty_trading_agent.src.data_ingestion.data_collector import DataCollector
from nifty_trading_agent.src.preprocessing.data_cleaner import DataCleaner
from nifty_trading_agent.src.preprocessing.feature_engineer import FeatureEngineer
from nifty_trading_agent.src.sentiment_analysis.news_collector import NewsCollector
from nifty_trading_agent.src.sentiment_analysis.social_media_collector import SocialMediaCollector
from nifty_trading_agent.src.sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
from nifty_trading_agent.src.market_analysis.volatility_analyzer import VolatilityAnalyzer
from nifty_trading_agent.src.market_analysis.correlation_analyzer import CorrelationAnalyzer
from nifty_trading_agent.src.options_pricing.black_scholes import BlackScholesModel
from nifty_trading_agent.src.risk_management.risk_calculator import RiskCalculator
from nifty_trading_agent.src.risk_management.position_sizer import PositionSizer
from nifty_trading_agent.src.rl_agent.trading_environment import TradingEnvironment
from nifty_trading_agent.src.rl_agent.dqn_agent import DQNAgent
from nifty_trading_agent.src.rl_agent.ppo_agent import PPOAgent
from nifty_trading_agent.src.rl_agent.ensemble_agent import EnsembleAgent
from nifty_trading_agent.src.paper_trading.paper_trading_engine import PaperTradingEngine
from nifty_trading_agent.src.paper_trading.performance_tracker import PerformanceTracker
from nifty_trading_agent.src.paper_trading.risk_monitor import RiskMonitor
from nifty_trading_agent.src.utils.config_manager import config
from nifty_trading_agent.src.utils.logger import logger
from nifty_trading_agent.src.utils.database import db_manager

class LiveDataTrainer:
    def __init__(self):
        self.zerodha_client = ZerodhaClient()
        self.data_collector = DataCollector()
        self.data_cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()
        self.news_collector = NewsCollector()
        self.social_media_collector = SocialMediaCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.volatility_analyzer = VolatilityAnalyzer()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.black_scholes_model = BlackScholesModel()
        self.risk_calculator = RiskCalculator()
        self.position_sizer = PositionSizer()
        
        self.dqn_agent = DQNAgent(state_dim=config.get("rl_agent.state_space_dim"), action_dim=config.get("rl_agent.action_space_dim"))
        self.ppo_agent = PPOAgent(state_dim=config.get("rl_agent.state_space_dim"), action_dim=config.get("rl_agent.action_space_dim"))
        self.ensemble_agent = EnsembleAgent([self.dqn_agent, self.ppo_agent])

        self.paper_trading_engine = PaperTradingEngine(initial_capital=config.get("trading.initial_capital"))
        self.performance_tracker = PerformanceTracker(self.paper_trading_engine)
        self.risk_monitor = RiskMonitor(self.paper_trading_engine)

        self.model_save_path = config.get("rl_agent.model_save_path")

        logger.info("LiveDataTrainer initialized.")

    def _get_zerodha_access_token(self):
        # This function will guide the user through the Zerodha login process
        # if an access token is not already available.
        if self.zerodha_client.access_token:
            logger.info("Zerodha access token already available.")
            return True

        login_url = self.zerodha_client.get_login_url()
        logger.info(f"Please visit this URL to log in to Zerodha: {login_url}")
        request_token = input("After logging in, paste the request token from the URL here: ")
        
        if self.zerodha_client.generate_session(request_token):
            logger.info("Zerodha session successfully generated.")
            return True
        else:
            logger.error("Failed to generate Zerodha session.")
            return False

    def run_trainer(self, historical_data_dir=None):
        logger.info("Starting LiveDataTrainer...")

        # 1. Load existing models if available (from local path, e.g., Kaggle output dir)
        dqn_model_path = os.path.join(self.model_save_path, "dqn_agent.zip")
        ppo_model_path = os.path.join(self.model_save_path, "ppo_agent.zip")
        
        if os.path.exists(dqn_model_path):
            self.dqn_agent.load_model(dqn_model_path)
            logger.info(f"Loaded existing DQN model from {dqn_model_path}")
        if os.path.exists(ppo_model_path):
            self.ppo_agent.load_model(ppo_model_path)
            logger.info(f"Loaded existing PPO model from {ppo_model_path}")

        # 2. Data Collection and Preprocessing
        market_data_df = pd.DataFrame()
        if historical_data_dir: # Use Kaggle data if provided
            logger.info(f"Loading historical data from Kaggle directory: {historical_data_dir}")
            all_files = []
            for root, _, files in os.walk(historical_data_dir):
                for file in files:
                    if file.endswith('.csv'):
                        all_files.append(os.path.join(root, file))
            
            if not all_files:
                logger.warning(f"No CSV files found in {historical_data_dir}. Cannot load Kaggle data.")
            else:
                list_dfs = []
                for f in all_files:
                    try:
                        df = pd.read_csv(f)
                        # Assuming columns like 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'
                        # Adjust column names if necessary based on actual Kaggle dataset
                        if 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp'])
                        elif 'date' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['date'])
                        else:
                            logger.warning(f"Timestamp column not found in {f}. Skipping.")
                            continue
                        list_dfs.append(df)
                    except Exception as e:
                        logger.error(f"Error reading {f}: {e}")
                
                if list_dfs:
                    market_data_df = pd.concat(list_dfs, ignore_index=True)
                    market_data_df = market_data_df.sort_values('timestamp').reset_index(drop=True)
                    logger.info(f"Loaded {len(market_data_df)} rows from Kaggle dataset.")
                else:
                    logger.warning("No data loaded from Kaggle CSVs.")

        
        if market_data_df.empty:
            logger.info("No Kaggle historical data loaded or available. Attempting to fetch from Zerodha.")
            if not self._get_zerodha_access_token():
                logger.error("Cannot proceed without Zerodha access token. Exiting trainer.")
                return
            
            # Fetch historical data from Zerodha (e.g., Nifty 50)
            # You'll need to get the instrument token for Nifty 50 or Bank Nifty
            # For simplicity, let's use a placeholder instrument token
            nifty_instrument_token = 738561 # Example Nifty 50 instrument token
            to_date = datetime.now().date()
            from_date = to_date - timedelta(days=365) # Last 1 year data
            market_data_df = self.data_collector.collect_historical_data(nifty_instrument_token, from_date, to_date, "day")

        if market_data_df.empty:
            logger.error("No historical data available for training. Exiting trainer.")
            return

        market_data_df = self.data_cleaner.clean_market_data(market_data_df)
        market_data_df = self.feature_engineer.add_technical_indicators(market_data_df)
        market_data_df = self.feature_engineer.add_volatility_features(market_data_df)
        # Placeholder for options and sentiment features (these would be merged based on timestamp)
        market_data_df = self.feature_engineer.add_options_features(market_data_df)
        market_data_df = self.feature_engineer.add_sentiment_features(market_data_df)
        
        # Drop any rows with NaN values after feature engineering
        market_data_df.dropna(inplace=True)

        if market_data_df.empty:
            logger.error("Market data is empty after feature engineering. Exiting trainer.")
            return

        # Prepare RL environment
        state_space_df = self.feature_engineer.create_rl_state_space(market_data_df)
        env = TradingEnvironment(market_data_df, state_space_df, self.paper_trading_engine, self.risk_calculator, self.position_sizer)

        # 3. RL Agent Training Loop
        num_episodes = config.get("rl_agent.training_episodes")
        for episode in range(num_episodes):
            obs = env.reset()
            done = False
            total_reward = 0
            step = 0

            while not done:
                # Get action from ensemble agent
                action = self.ensemble_agent.select_action(obs)
                
                # Execute action in environment
                next_obs, reward, done, info = env.step(action)
                
                # Store experience (for DQN)
                self.dqn_agent.store_experience(obs, action, reward, next_obs, done)
                
                # Update agents
                self.dqn_agent.update_model()
                self.ppo_agent.update_model(obs, action, reward, next_obs, done) # PPO updates differently

                obs = next_obs
                total_reward += reward
                step += 1

                # In a real live trainer, you'd fetch live data here and update the environment
                # For now, we're iterating through the historical data.
                # To simulate live data, you'd fetch new data points and append to market_data_df
                # and then update the environment's internal state.

            logger.info(f"Episode {episode + 1}/{num_episodes}, Total Reward: {total_reward}, Steps: {step}")
            
            # Evaluate and save models periodically
            if (episode + 1) % 100 == 0:
                accuracy = self.performance_tracker.calculate_accuracy() # Placeholder
                logger.info(f"Episode {episode + 1}: Current Accuracy: {accuracy:.2f}")
                
                # Ensure model_save_path exists
                os.makedirs(self.model_save_path, exist_ok=True)

                self.dqn_agent.save_model(dqn_model_path)
                self.ppo_agent.save_model(ppo_model_path)
                
                db_manager.add_model_checkpoint({
                    "model_name": "ensemble_agent",
                    "model_path": self.model_save_path, # Store local path
                    "accuracy": accuracy,
                    "success_rate": accuracy # Assuming accuracy is success rate for now
                })

        logger.info("LiveDataTrainer finished.")

if __name__ == "__main__":
    trainer = LiveDataTrainer()
    # When running in Kaggle, you'd pass the path to the Kaggle dataset here
    # For example: trainer.run_trainer(historical_data_dir="/kaggle/input/indian-nifty-and-banknifty-options-data-2020-2024/")
    # The actual path will depend on the dataset structure.
    trainer.run_trainer() # This will attempt to fetch from Zerodha if no path is given


