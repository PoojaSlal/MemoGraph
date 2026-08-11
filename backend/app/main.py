from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.logging import setup_logging


setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MemoGraph API starting")
    yield
    logger.info("MemoGraph API shutting down")


app = FastAPI(
    title="MemoGraph API",
    version="0.1.0",
    description="Context-aware personal AI memory retrieval system.",
    lifespan=lifespan,
)

app.include_router(health_router)


@app.get("/")
def root():
    logger.info("Root endpoint accessed")

    return {
        "name": "MemoGraph",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/test")
def test():
    logger.info("Test endpoint accessed")

    return {
        "status": "working"
    }