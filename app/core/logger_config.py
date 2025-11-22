# app/core/logger_config.py
from loguru import logger


def get_logger():
    logger.add(
        "logs/chatbot.log",
        rotation="10 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )
    return logger
