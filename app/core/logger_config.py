# app/core/logger_config.py
from loguru import logger
from app.core.config import Settings

def get_logger():
    settings = Settings()  # ← cria uma instância local de configuração
    logger.add(
        "logs/chatbot.log",
        rotation="10 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    return logger
