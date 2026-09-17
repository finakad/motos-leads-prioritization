from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1 import etl, leads
from app.core.config import get_settings
from app.core.database import engine

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(leads.router, prefix="/api/v1")
app.include_router(etl.router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.get("/health/database")
def database_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "ok"}