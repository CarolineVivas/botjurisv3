# app/core/queue_config.py
import os
from dotenv import load_dotenv
from redis import Redis
from rq import Queue
from app.core.logger_config import get_logger

load_dotenv()
log = get_logger()

# 🔗 Conexão com o Redis (mesmo usado no cache)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("botjuris", connection=redis_conn)

log.info(f"Queue configurada e conectada ao Redis: {REDIS_URL}")

