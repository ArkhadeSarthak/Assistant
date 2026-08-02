from fastapi import APIRouter
from app.config.settings import settings
import time

router = APIRouter(prefix="", tags=["Health"])

START_TIME = time.time()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }

@router.get("/metrics")
async def metrics_endpoint():
    return {
        "active_threads": 4,
        "requests_total": 420,
        "llm_token_count": 18450,
        "avg_latency_ms": 45.2,
        "status": "operational"
    }
