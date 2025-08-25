from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ..utils.config_manager import config
from ..utils.logger import logger

Base = declarative_base()

class MarketData(Base):
    __tablename__ = 'market_data'
    id = Column(Integer, primary_key=True)
    instrument_token = Column(Integer, nullable=False)
    tradingsymbol = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    oi = Column(Integer) # Open Interest

class SentimentData(Base):
    __tablename__ = 'sentiment_data'
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    text = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    sentiment_magnitude = Column(Float)
    keywords = Column(Text) # Comma separated keywords

class TradeLog(Base):
    __tablename__ = 'trade_log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    tradingsymbol = Column(String(50), nullable=False)
    transaction_type = Column(String(10), nullable=False) # BUY/SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    order_id = Column(String(100))
    status = Column(String(50))
    pnl = Column(Float)
    is_paper_trade = Column(Boolean, default=True)

class PerformanceMetric(Base):
    __tablename__ = 'performance_metrics'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    metric_name = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    period = Column(String(20)) # e.g., daily, weekly, all_time

class RiskMetric(Base):
    __tablename__ = 'risk_metrics'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    metric_name = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)

class ModelCheckpoint(Base):
    __tablename__ = 'model_checkpoints'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_path = Column(String(255), nullable=False)
    accuracy = Column(Float)
    success_rate = Column(Float)

class DatabaseManager:
    def __init__(self):
        db_type = config.get("database.type")
        db_path = config.get("database.path")

        if db_type == "sqlite":
            self.engine = create_engine(f"sqlite:///{db_path}")
        elif db_type == "postgresql":
            # Assuming db_path is a connection string for PostgreSQL
            self.engine = create_engine(db_path)
        elif db_type == "mongodb":
            # MongoDB would require a different ODM (e.g., MongoEngine, Pymongo)
            # For simplicity, we'll stick to SQL-based for now.
            logger.error("MongoDB not directly supported with SQLAlchemy Base. Use a different ODM.")
            raise NotImplementedError("MongoDB support not implemented yet.")
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"DatabaseManager initialized with {db_type} at {db_path}")

    def get_session(self):
        return self.Session()

    def add_market_data(self, data):
        session = self.get_session()
        try:
            market_data = MarketData(**data)
            session.add(market_data)
            session.commit()
            logger.debug(f"Added market data for {data.get("tradingsymbol")}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding market data: {e}")
        finally:
            session.close()

    def add_sentiment_data(self, data):
        session = self.get_session()
        try:
            sentiment_data = SentimentData(**data)
            session.add(sentiment_data)
            session.commit()
            logger.debug(f"Added sentiment data from {data.get("source")}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding sentiment data: {e}")
        finally:
            session.close()

    def add_trade_log(self, data):
        session = self.get_session()
        try:
            trade_log = TradeLog(**data)
            session.add(trade_log)
            session.commit()
            logger.debug(f"Added trade log for {data.get("tradingsymbol")}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding trade log: {e}")
        finally:
            session.close()

    def add_performance_metric(self, data):
        session = self.get_session()
        try:
            metric = PerformanceMetric(**data)
            session.add(metric)
            session.commit()
            logger.debug(f"Added performance metric {data.get("metric_name")}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding performance metric: {e}")
        finally:
            session.close()

    def add_risk_metric(self, data):
        session = self.get_session()
        try:
            metric = RiskMetric(**data)
            session.add(metric)
            session.commit()
            logger.debug(f"Added risk metric {data.get("metric_name")}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding risk metric: {e}")
        finally:
            session.close()

    def add_model_checkpoint(self, data):
        session = self.get_session()
        try:
            checkpoint = ModelCheckpoint(**data)
            session.add(checkpoint)
            session.commit()
            logger.debug(f"Added model checkpoint for {data.get("model_name")}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding model checkpoint: {e}")
        finally:
            session.close()

    def get_latest_model_checkpoint(self, model_name):
        session = self.get_session()
        try:
            checkpoint = session.query(ModelCheckpoint).filter_by(model_name=model_name).order_by(ModelCheckpoint.timestamp.desc()).first()
            return checkpoint
        except Exception as e:
            logger.error(f"Error getting latest model checkpoint: {e}")
            return None
        finally:
            session.close()


db_manager = DatabaseManager()


