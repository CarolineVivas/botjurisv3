# app/routers/health.py
"""
Rotas de health check e métricas.
"""
from fastapi import APIRouter

from app.core.health import get_health, get_liveness, get_readiness
from app.core.metrics import metrics

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check completo da aplicação.

    Verifica todos os serviços: database, Redis, OpenAI, Evolution API.

    Returns:
        Status de saúde de todos os serviços
    """
    return await get_health()


@router.get("/health/live")
async def liveness_probe():
    """
    Liveness probe para Kubernetes/Docker.

    Verifica se a aplicação está viva.
    Usado para decidir se precisa reiniciar o container.

    Returns:
        Status simples (alive)
    """
    return await get_liveness()


@router.get("/health/ready")
async def readiness_probe():
    """
    Readiness probe para Kubernetes/Docker.

    Verifica se a aplicação está pronta para receber tráfego.
    Usado para load balancing.

    Returns:
        Status de prontidão (ready/not_ready)
    """
    return await get_readiness()


@router.get("/metrics")
async def get_metrics():
    """
    Retorna métricas da aplicação.

    Inclui estatísticas de:
    - Requisições HTTP
    - Mensagens processadas
    - Uso de IA
    - Cache hits/misses
    - Fila de processamento
    - Latências

    Returns:
        Métricas detalhadas
    """
    return metrics.get_metrics()


@router.post("/metrics/reset")
async def reset_metrics():
    """
    Reseta todas as métricas.

    Útil para testes ou reiniciar contadores.

    Returns:
        Confirmação de reset
    """
    metrics.reset()
    return {"status": "metrics_reset", "message": "Todas as métricas foram resetadas"}
