import sys
from loguru import logger
from app.config.settings import settings

def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
    )
    logger.add(
        "logs/aura_ai.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        enqueue=True,
    )
    return logger

app_logger = setup_logger()
