from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1 import advisors, etl, leads
from app.core.config import get_settings
from app.core.database import engine

settings = get_settings()

tags_metadata = [
    {
        "name": "Leads Prioritization",
        "description": "Consulta de leads priorizados, detalles operativos, conversaciones, señales IA y desglose explicable del score.",
    },
    {
        "name": "ETL Pipeline",
        "description": "Auditoría y disparo de pipelines de ingesta y procesamiento de datos.",
    },
    {
        "name": "Health",
        "description": "Verificación de salud y disponibilidad del servicio y PostgreSQL.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API Backend para la priorización y explicabilidad de prospectos (leads) de motocicletas, "
        "con estricto aislamiento multitenant por compañía y calibración estadística histórica."
    ),
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(leads.router, prefix="/api/v1")
app.include_router(advisors.router, prefix="/api/v1")
app.include_router(etl.router, prefix="/api/v1")



@app.get(
    "/health",
    tags=["Health"],
    summary="Health check del servicio",
    description="Retorna el estado operativo del servicio y el ambiente activo.",
)
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.get(
    "/health/database",
    tags=["Health"],
    summary="Health check de la base de datos",
    description="Ejecuta una consulta de verificación de conectividad contra PostgreSQL.",
)
def database_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "ok"}