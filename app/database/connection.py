# app/database/connection.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from time import perf_counter

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🚀 Connection Pool otimizado
engine = create_engine(
    DATABASE_URL,
    echo=False,                # mantenha False em produção
    pool_size=10,              # conexões persistentes
    max_overflow=20,           # extras temporárias
    pool_pre_ping=True,        # detecta conexões mortas
    pool_recycle=1800,         # recicla após 30 min
    connect_args={"sslmode": "require"}  # p/ Supabase
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    return SessionLocal()

# 🧠 Query profiling (tempo de execução)
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(perf_counter())

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = perf_counter() - conn.info['query_start_time'].pop(-1)
    print(f"⏱️ Query executada em {total:.3f}s")
