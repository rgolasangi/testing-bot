# Nifty and Bank Nifty Option Trading Agent

This is a super smart Nifty and Bank Nifty option trading agent that leverages Reinforcement Learning (RL), Deep Learning (DL), Sentiment Analysis, Market Analysis, and Option Greeks for automated trading. It integrates with Zerodha for live market data and trading.

## Features

- **Reinforcement Learning**: Utilizes DQN and PPO agents for optimal trading decisions.
- **Deep Learning**: Advanced neural networks for pattern recognition and prediction.
- **Sentiment Analysis**: Integrates news and social media sentiment for market insights.
- **Market Analysis**: Volatility, correlation, and other advanced market metrics.
- **Option Greeks**: Calculates and utilizes Delta, Gamma, Theta, Vega, and Rho for options pricing and risk management.
- **Zerodha Integration**: Connects to Zerodha Kite Connect API for live data and trade execution.
- **Live Data Training**: Agents train on real-time and historical market data from Zerodha.
- **Paper Trading**: Allows agents to practice and validate strategies in a simulated environment until a target accuracy is reached.
- **Risk Management**: Comprehensive risk controls including drawdown limits, position sizing, and automated circuit breakers.
- **Performance Tracking**: Detailed analytics and reporting of trading performance.
- **Monitoring Dashboard**: A real-time React-based dashboard for monitoring agent status, portfolio, and performance.
- **Production Ready**: Designed for robust deployment with Docker, systemd, and cloud platforms (GCP, Render).

## Architecture Overview

### 1. Data Ingestion

- **ZerodhaClient**: Handles all interactions with the Zerodha Kite Connect API for fetching historical data, real-time quotes, and executing trades.
- **DataCollector**: Collects and manages market data from various sources.

### 2. Preprocessing

- **DataCleaner**: Cleans and preprocesses raw market data.
- **FeatureEngineer**: Generates technical indicators, options features, and other relevant features for the RL agent.

### 3. Sentiment Analysis

- **NewsCollector**: Gathers financial news from multiple sources (NewsAPI, Alpha Vantage, RSS feeds).
- **SocialMediaCollector**: Collects sentiment data from social media platforms (Twitter, Reddit).
- **SentimentAnalyzer**: Processes collected text data to derive sentiment scores using NLP models (VADER, TextBlob, FinBERT).

### 4. Market Analysis

- **VolatilityAnalyzer**: Calculates various volatility metrics (historical, Parkinson, Garman-Klass) and identifies market regimes.
- **CorrelationAnalyzer**: Analyzes correlations between market movements, sentiment, and other factors.

### 5. Options Pricing & Risk Management

- **BlackScholesModel**: Implements the Black-Scholes model for options pricing and Greeks calculation (Delta, Gamma, Theta, Vega, Rho).
- **RiskCalculator**: Computes various risk metrics (VaR, Expected Shortfall, Max Drawdown) and performs stress testing.
- **PositionSizer**: Determines optimal position sizes based on risk appetite and market conditions.

### 6. Reinforcement Learning Agent

- **TradingEnvironment**: A custom Gymnasium-compatible environment simulating Nifty/Bank Nifty options trading.
- **DQN/PPO Agents**: Implement Deep Q-Network and Proximal Policy Optimization algorithms.
- **EnsembleAgent**: Combines multiple RL agents for robust decision-making.
- **TrainingPipeline**: Manages the training process, including data loading, model updates, and evaluation.

### 7. Paper Trading & Live Trading

- **PaperTradingEngine**: Simulates trades in a virtual portfolio using live market data.
- **MarketDataFeed**: Provides real-time market data to the paper trading engine.
- **PerformanceTracker**: Tracks and reports key performance metrics (Sharpe Ratio, Win Rate, Drawdown).
- **RiskMonitor**: Monitors real-time risk metrics and triggers alerts/circuit breakers.
- **LiveDataTrainer**: Orchestrates continuous training and fine-tuning of RL models with live data.

### 8. Monitoring Dashboard

- **Trading Dashboard (Flask Backend)**: Provides REST APIs for the frontend to fetch real-time data, performance metrics, risk status, and control trading operations.
- **Trading Frontend (React)**: A responsive web interface for visualizing portfolio performance, market data, sentiment, and managing the trading agent.

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js (for frontend)
- Git
- Zerodha Kite Connect API Key, API Secret, and Access Token
- NewsAPI Key (optional, for news sentiment)
- Alpha Vantage API Key (optional, for news sentiment)
- Twitter API Credentials (optional, for social media sentiment)
- Reddit API Credentials (optional, for social media sentiment)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/nifty-trading-agent.git
cd nifty-trading-agent
```

### 2. Environment Variables

Create a `.env` file in the `nifty_trading_agent` directory based on `.env.example` and fill in your API credentials:

```
ZERODHA_API_KEY=YOUR_ZERODHA_API_KEY
ZERODHA_API_SECRET=YOUR_ZERODHA_API_SECRET
ZERODHA_ACCESS_TOKEN=YOUR_ZERODHA_ACCESS_TOKEN
NEWS_API_KEY=YOUR_NEWS_API_KEY
ALPHA_VANTAGE_API_KEY=YOUR_ALPHA_VANTAGE_API_KEY
TWITTER_CONSUMER_KEY=YOUR_TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET=YOUR_TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN=YOUR_TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET=YOUR_TWITTER_ACCESS_TOKEN_SECRET
REDDIT_CLIENT_ID=YOUR_REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET=YOUR_REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT=YOUR_REDDIT_USER_AGENT
```

### 3. Install Dependencies

```bash
# Backend (Python)
pip install -r nifty_trading_agent/requirements.txt

# Frontend (Node.js)
cd trading_frontend
npm install
cd ..
```

### 4. Prepare for Deployment (using `deploy.sh`)

The `deploy.sh` script automates the setup for various deployment options, including generating `render.yaml` for Render deployment.

```bash
chmod +x deploy.sh
./deploy.sh
```

This script will:
- Build the React frontend.
- Generate `render.yaml` for Render deployment, defining the Flask backend as a Web Service and the React frontend as a Static Site.
- Generate Docker-related files (`Dockerfile`, `docker-compose.yml`) for local Docker deployment.
- Generate `systemd` service files for Linux server deployment.

## Deployment Options

### A. Deploying to Render (Recommended for Free Tier)

1.  **Push to GitHub**: Ensure your project is pushed to a GitHub repository (as you've done).
2.  **Connect Render**: Log in to your Render account. Create a new Web Service and a new Static Site.
3.  **Select Repository**: Connect both services to your GitHub repository.
4.  **Configure Web Service (Flask Backend)**:
    *   **Root Directory**: `trading_dashboard`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn -w 4 -b 0.0.0.0:10000 main:app` (or `python main.py` for development)
    *   **Environment Variables**: Add your Zerodha API keys and other secrets from your `.env` file here.
5.  **Configure Static Site (React Frontend)**:
    *   **Root Directory**: `trading_frontend`
    *   **Build Command**: `npm install && npm run build`
    *   **Publish Directory**: `dist` (or `build` depending on your React setup)
    *   **Environment Variables**: If your frontend needs any environment variables (e.g., API endpoint URL), add them here.
6.  **Deploy**: Trigger the deployments on Render.

### B. Local Docker Deployment

After running `./deploy.sh`, navigate to the `trading_dashboard` directory and use Docker Compose:

```bash
cd trading_dashboard
docker-compose up --build -d
```

### C. Linux Server (Systemd) Deployment

After running `./deploy.sh`, copy the generated `nifty-trading-agent.service` file to `/etc/systemd/system/` and enable/start it.

## Training the RL Agent (using Google Colab)

The `nifty_trading_agent_colab_training.ipynb` notebook is designed for training your RL agent using Google Colab's free GPU resources.

1.  **Open in Colab**: Upload `nifty_trading_agent_colab_training.ipynb` to your Google Drive and open it with Google Colab.
2.  **Connect to GPU Runtime**: Go to `Runtime -> Change runtime type` and select `GPU` as the hardware accelerator.
3.  **Follow Notebook Instructions**: The notebook provides step-by-step guidance on:
    *   Cloning your GitHub repository.
    *   Installing dependencies.
    *   Connecting to Google Drive for model persistence.
    *   Securely setting your Zerodha API keys using Colab's `Secrets` feature.
    *   Running the `live_data_trainer.py` script for historical and live data training.
    *   Saving the trained models to your Google Drive folder.

**Important**: The Flask backend deployed on Render will be configured to load the latest trained model from your Google Drive. Ensure the path configured in the Flask app matches where Colab saves the models.

## Running the Agent

Once the backend and frontend are deployed (e.g., on Render) and your RL model is trained via Google Colab and saved to Google Drive:

1.  Access the deployed React frontend URL in your browser.
2.  Monitor the dashboard for real-time portfolio, market, and risk metrics.
3.  Use the dashboard controls to start paper trading. The agent will load the trained model and begin making simulated trades.
4.  Once the agent achieves the target accuracy (e.g., 90% success rate), you can enable live trading (with extreme caution and proper risk management).

## Risk Management and Safety

This agent includes robust risk management features:
- **Paper Trading First**: Mandatory paper trading until 90% accuracy.
- **Max Drawdown Limits**: Configurable limits to prevent significant losses.
- **Daily Loss Limits**: Stops trading if daily loss exceeds a threshold.
- **Position Sizing**: Dynamically adjusts trade sizes based on risk.
- **Circuit Breakers**: Automated halts in extreme market conditions.
- **Alerts**: Email notifications for critical events.

**Always exercise extreme caution when engaging in live trading. Automated systems require continuous monitoring and adjustments.**

## Contributing

Feel free to fork the repository, submit pull requests, or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


