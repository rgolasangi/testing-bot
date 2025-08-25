from loguru import logger
from .config_manager import config

logger.add(config.get("logging.file"), rotation="500 MB")


