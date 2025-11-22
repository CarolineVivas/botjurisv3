# app/core/metrics.py
"""
Métricas para monitoramento da aplicação.
Coleta estatísticas de uso, performance e erros.
"""
import time
from datetime import datetime
from typing import Any

from app.core.logger_config import get_logger

log = get_logger()


class MetricsCollector:
    """Coleta e armazena métricas da aplicação."""

    def __init__(self):
        self.start_time = datetime.now()
        self._reset_metrics()

    def _reset_metrics(self):
        """Reseta todas as métricas."""
        self.metrics = {
            # Contadores de requisições
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            # Contadores de mensagens
            "messages_received": 0,
            "messages_processed": 0,
            "messages_failed": 0,
            # Contadores de IA
            "ia_requests": 0,
            "ia_tokens_used": 0,
            "ia_errors": 0,
            # Contadores de cache
            "cache_hits": 0,
            "cache_misses": 0,
            # Contadores de queue
            "queue_enqueued": 0,
            "queue_processed": 0,
            "queue_failed": 0,
            "queue_retries": 0,
            # Latências (em ms)
            "latency_webhook_avg": 0,
            "latency_ia_avg": 0,
            "latency_db_avg": 0,
            # Listas para calcular médias
            "_latency_webhook_samples": [],
            "_latency_ia_samples": [],
            "_latency_db_samples": [],
        }

    def increment(self, metric: str, value: int = 1) -> None:
        """
        Incrementa um contador.

        Args:
            metric: Nome da métrica
            value: Valor a incrementar (default: 1)
        """
        if metric in self.metrics:
            self.metrics[metric] += value
        else:
            log.warning(f"⚠️ Métrica desconhecida: {metric}")

    def record_latency(self, metric_type: str, latency_ms: float) -> None:
        """
        Registra uma latência.

        Args:
            metric_type: Tipo (webhook, ia, db)
            latency_ms: Latência em milissegundos
        """
        sample_key = f"_latency_{metric_type}_samples"
        avg_key = f"latency_{metric_type}_avg"

        if sample_key in self.metrics:
            samples = self.metrics[sample_key]
            samples.append(latency_ms)

            # Manter apenas últimas 100 amostras
            if len(samples) > 100:
                samples.pop(0)

            # Calcular média
            self.metrics[avg_key] = round(sum(samples) / len(samples), 2)

    def track_request(self, success: bool = True) -> None:
        """Registra uma requisição HTTP."""
        self.increment("requests_total")
        if success:
            self.increment("requests_success")
        else:
            self.increment("requests_error")

    def track_message(self, status: str = "received") -> None:
        """
        Registra uma mensagem.

        Args:
            status: received, processed, failed
        """
        if status == "received":
            self.increment("messages_received")
        elif status == "processed":
            self.increment("messages_processed")
        elif status == "failed":
            self.increment("messages_failed")

    def track_ia(self, tokens: int = 0, success: bool = True) -> None:
        """
        Registra uma chamada à IA.

        Args:
            tokens: Tokens usados
            success: Se foi bem-sucedida
        """
        self.increment("ia_requests")
        self.increment("ia_tokens_used", tokens)
        if not success:
            self.increment("ia_errors")

    def track_cache(self, hit: bool = True) -> None:
        """
        Registra acesso ao cache.

        Args:
            hit: True se encontrou no cache
        """
        if hit:
            self.increment("cache_hits")
        else:
            self.increment("cache_misses")

    def track_queue(self, action: str = "enqueued") -> None:
        """
        Registra ação na fila.

        Args:
            action: enqueued, processed, failed, retry
        """
        if action == "enqueued":
            self.increment("queue_enqueued")
        elif action == "processed":
            self.increment("queue_processed")
        elif action == "failed":
            self.increment("queue_failed")
        elif action == "retry":
            self.increment("queue_retries")

    def get_metrics(self) -> dict[str, Any]:
        """
        Retorna todas as métricas.

        Returns:
            Dict com métricas
        """
        # Calcular uptime
        uptime_seconds = int((datetime.now() - self.start_time).total_seconds())

        # Calcular taxas
        total_requests = self.metrics["requests_total"] or 1
        success_rate = round(
            (self.metrics["requests_success"] / total_requests) * 100, 2
        )

        total_messages = self.metrics["messages_received"] or 1
        message_success_rate = round(
            (self.metrics["messages_processed"] / total_messages) * 100, 2
        )

        cache_total = (self.metrics["cache_hits"] + self.metrics["cache_misses"]) or 1
        cache_hit_rate = round((self.metrics["cache_hits"] / cache_total) * 100, 2)

        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "requests": {
                "total": self.metrics["requests_total"],
                "success": self.metrics["requests_success"],
                "error": self.metrics["requests_error"],
                "success_rate_percent": success_rate,
            },
            "messages": {
                "received": self.metrics["messages_received"],
                "processed": self.metrics["messages_processed"],
                "failed": self.metrics["messages_failed"],
                "success_rate_percent": message_success_rate,
            },
            "ia": {
                "requests": self.metrics["ia_requests"],
                "tokens_used": self.metrics["ia_tokens_used"],
                "errors": self.metrics["ia_errors"],
            },
            "cache": {
                "hits": self.metrics["cache_hits"],
                "misses": self.metrics["cache_misses"],
                "hit_rate_percent": cache_hit_rate,
            },
            "queue": {
                "enqueued": self.metrics["queue_enqueued"],
                "processed": self.metrics["queue_processed"],
                "failed": self.metrics["queue_failed"],
                "retries": self.metrics["queue_retries"],
            },
            "latency_ms": {
                "webhook_avg": self.metrics["latency_webhook_avg"],
                "ia_avg": self.metrics["latency_ia_avg"],
                "db_avg": self.metrics["latency_db_avg"],
            },
        }

    def reset(self) -> None:
        """Reseta todas as métricas (útil para testes)."""
        self._reset_metrics()
        log.info("📊 Métricas resetadas")


# Instância global
metrics = MetricsCollector()


# Context manager para medir latência
class LatencyTimer:
    """Context manager para medir latência automaticamente."""

    def __init__(self, metric_type: str):
        self.metric_type = metric_type
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            latency_ms = (time.time() - self.start_time) * 1000
            metrics.record_latency(self.metric_type, latency_ms)


# Exemplo de uso:
# with LatencyTimer("webhook"):
#     process_webhook(data)
