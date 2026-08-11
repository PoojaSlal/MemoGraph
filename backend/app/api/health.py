import logging

from fastapi import APIRouter, HTTPException

from app.db.postgres import get_connection
from app.services.qdrant import qdrant_client
from app.services.memgraph import verify_connection as verify_memgraph
from app.services.redis import verify_connection as verify_redis


router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/health")
def health_check():
    services = {}

    # PostgreSQL
    try:
        connection = get_connection()
        connection.close()
        services["postgresql"] = "healthy"
    except Exception as exc:
        services["postgresql"] = "unhealthy"
        logger.exception("PostgreSQL health check failed: %s", exc)

    # Qdrant
    try:
        qdrant_client.get_collections()
        services["qdrant"] = "healthy"
    except Exception as exc:
        services["qdrant"] = "unhealthy"
        logger.exception("Qdrant health check failed: %s", exc)

    # Memgraph
    try:
        verify_memgraph()
        services["memgraph"] = "healthy"
    except Exception as exc:
        services["memgraph"] = "unhealthy"
        logger.exception("Memgraph health check failed: %s", exc)

    # Redis
    try:
        verify_redis()
        services["redis"] = "healthy"
    except Exception as exc:
        services["redis"] = "unhealthy"
        logger.exception("Redis health check failed: %s", exc)

    all_healthy = all(
        status == "healthy"
        for status in services.values()
    )

    if not all_healthy:
        logger.error(
            "MemoGraph health check failed: %s",
            services,
        )

        raise HTTPException(
            status_code=503,
            detail={
                "status": "degraded",
                "services": services,
            },
        )

    return {
        "status": "healthy",
        "services": services,
    }