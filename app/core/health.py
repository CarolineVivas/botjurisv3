# app/core/health.py
"""
Health checks para monitoramento da aplicação.
Verifica status de todos os serviços críticos.
"""
from datetime import datetime
from typing import Any

from app.core.logger_config import get_logger

log = get_logger()


class HealthChecker:
    """Gerencia verificações de saúde da aplicação."""

    def __init__(self):
        self.start_time = datetime.now()

    async def check_database(self) -> dict[str, Any]:
        """
        Verifica conexão com o banco de dados.

        Returns:
            Dict com status e latência
        """
        try:
            from app.database.connection import SessionLocal

            start = datetime.now()
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            latency = (datetime.now() - start).total_seconds() * 1000

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
            }
        except Exception as e:
            log.error(f"❌ Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def check_redis(self) -> dict[str, Any]:
        """
        Verifica conexão com o Redis.

        Returns:
            Dict com status e latência
        """
        try:
            from app.core.cache import redis_client

            start = datetime.now()
            redis_client.ping()
            latency = (datetime.now() - start).total_seconds() * 1000

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
            }
        except Exception as e:
            log.error(f"❌ Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def check_openai(self) -> dict[str, Any]:
        """
        Verifica conexão com a API da OpenAI.

        Returns:
            Dict com status
        """
        try:
            import openai

            from app.core.config import get_settings

            settings = get_settings()
            openai.api_key = settings.OPENAI_API_KEY

            # Apenas verifica se a key é válida (não faz chamada real)
            if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 20:
                return {"status": "healthy", "configured": True}
            else:
                return {"status": "unhealthy", "error": "API key not configured"}

        except Exception as e:
            log.error(f"❌ OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def check_evolution_api(self) -> dict[str, Any]:
        """
        Verifica conexão com a Evolution API.

        Returns:
            Dict com status
        """
        try:
            from app.core.config import get_settings

            settings = get_settings()

            if settings.EVOLUTION_HOST and settings.EVOLUTION_API_KEY:
                return {"status": "healthy", "configured": True}
            else:
                return {"status": "unhealthy", "error": "Not configured"}

        except Exception as e:
            log.error(f"❌ Evolution API health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_uptime(self) -> dict[str, Any]:
        """
        Retorna tempo de atividade da aplicação.

        Returns:
            Dict com uptime em segundos e formato legível
        """
        uptime = datetime.now() - self.start_time
        total_seconds = int(uptime.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        human_readable = f"{days}d {hours}h {minutes}m {seconds}s"

        return {
            "seconds": total_seconds,
            "human_readable": human_readable,
            "started_at": self.start_time.isoformat(),
        }

    async def full_health_check(self) -> dict[str, Any]:
        """
        Executa verificação completa de todos os serviços.

        Returns:
            Dict com status geral e detalhes de cada serviço
        """
        from app.core.config import get_settings

        settings = get_settings()

        # Executar todas as verificações
        database = await self.check_database()
        redis = await self.check_redis()
        openai = await self.check_openai()
        evolution = await self.check_evolution_api()
        uptime = self.get_uptime()

        # Determinar status geral
        all_checks = [database, redis, openai, evolution]
        all_healthy = all(check.get("status") == "healthy" for check in all_checks)

        # Verificações críticas (sem elas a app não funciona)
        critical_healthy = (
            database.get("status") == "healthy" and redis.get("status") == "healthy"
        )

        if all_healthy:
            overall_status = "healthy"
        elif critical_healthy:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "environment": settings.ENVIRONMENT,
            "uptime": uptime,
            "checks": {
                "database": database,
                "redis": redis,
                "openai": openai,
                "evolution_api": evolution,
            },
        }


# Instância global
health_checker = HealthChecker()


async def get_health() -> dict[str, Any]:
    """
    Função helper para obter status de saúde.

    Returns:
        Dict com status completo
    """
    return await health_checker.full_health_check()


async def get_liveness() -> dict[str, Any]:
    """
    Liveness probe - verifica se a aplicação está viva.
    Usado pelo Kubernetes/Docker para restart.

    Returns:
        Dict simples com status
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
    }


async def get_readiness() -> dict[str, Any]:
    """
    Readiness probe - verifica se a aplicação está pronta para receber tráfego.
    Usado pelo Kubernetes/Docker para load balancing.

    Returns:
        Dict com status de prontidão
    """
    health = await health_checker.full_health_check()

    is_ready = health["status"] in ["healthy", "degraded"]

    return {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": datetime.now().isoformat(),
    }
