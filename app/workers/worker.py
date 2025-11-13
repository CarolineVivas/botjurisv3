# app/workers/worker.py
import signal
import sys
from rq import Worker, Queue
from app.core.queue_config import redis_conn

listen = ["botjuris"]

def handle_shutdown(signum, frame):
    print("🛑 Encerrando worker com segurança...")
    sys.exit(0)

def main():
    # graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    qs = [Queue(name, connection=redis_conn) for name in listen]
    print("👷 Worker iniciado e ouvindo fila:", listen)
    Worker(qs, connection=redis_conn).work(with_scheduler=True)

if __name__ == "__main__":
    main()


