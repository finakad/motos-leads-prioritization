from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import CompanyContext, get_company_context
from app.schemas.analysis import ConversationAnalysisResponse
from app.schemas.leads import (
    LeadConversationsResponse,
    LeadDetailResponse,
    PaginatedLeadsResponse,
)
from app.schemas.scoring import LeadScoreDetail, PrioritizationSummary
from app.services.lead_query_service import LeadQueryService
from app.services.prioritization_engine import PrioritizationEngine

router = APIRouter(
    prefix="/companies/{company_id}/leads",
    tags=["Leads Prioritization"],
)


@router.get(
    "/prioritized",
    response_model=PaginatedLeadsResponse,
    summary="Listar leads priorizados con filtros y paginación",
    description=(
        "Retorna el listado paginado y ordenado de leads priorizados estrictamente "
        "para la compañía especificada. Incluye filtros por sede, asesor, canal, "
        "estado operativo, tier de prioridad y rango de fechas. Aplica minimización "
        "de datos personales (PII enmascarado)."
    ),
)
def list_prioritized_leads(
    company_ctx: CompanyContext = Depends(get_company_context),
    sales_point_id: str | None = Query(
        None, description="Filtrar por ID del punto de venta o sede"
    ),
    advisor_id: str | None = Query(
        None, description="Filtrar por ID del asesor (resuelve a su sede asignada)"
    ),
    channel: str | None = Query(
        None, description="Filtrar por canal de adquisición (WhatsApp, Formulario Web, Meta Ads)"
    ),
    status: str | None = Query(
        None, description="Filtrar por estado operativo del lead (ej. Nuevo, Cotización enviada)"
    ),
    priority_tier: Literal["ALTA", "MEDIA", "BAJA"] | None = Query(
        None, description="Filtrar por tier de prioridad (ALTA, MEDIA, BAJA)"
    ),
    date_from: datetime | None = Query(
        None, description="Fecha de registro inicial (formato ISO 8601)"
    ),
    date_to: datetime | None = Query(
        None, description="Fecha de registro final (formato ISO 8601)"
    ),
    order_by: Literal["score", "registered_at", "customer_name"] = Query(
        "score", description="Campo de ordenamiento"
    ),
    order_direction: Literal["asc", "desc"] = Query(
        "desc", description="Dirección de ordenamiento ('asc' o 'desc')"
    ),
    page: int = Query(1, ge=1, description="Número de página (1-indexada)"),
    page_size: int = Query(20, ge=1, le=100, description="Cantidad de registros por página"),
    db: Session = Depends(get_db),
) -> PaginatedLeadsResponse:
    service = LeadQueryService()
    return service.list_prioritized_leads(
        session=db,
        company_id=company_ctx.company_id,
        sales_point_id=sales_point_id,
        advisor_id=advisor_id,
        channel=channel,
        status_filter=status,
        priority_tier=priority_tier,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_direction=order_direction,
    )


@router.get(
    "/{lead_id}",
    response_model=LeadDetailResponse,
    summary="Consultar detalle de un lead",
    description=(
        "Retorna la información operativa completa de un lead específico con "
        "datos de contacto enmascarados, garantizando estricto aislamiento multitenant. "
        "Si el lead pertenece a otra compañía o no existe, retorna 404 seguro."
    ),
)
def get_lead_detail(
    lead_id: str,
    company_ctx: CompanyContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> LeadDetailResponse:
    service = LeadQueryService()
    return service.get_lead_detail(
        session=db,
        company_id=company_ctx.company_id,
        lead_id=lead_id,
    )


@router.get(
    "/{lead_id}/conversations",
    response_model=LeadConversationsResponse,
    summary="Consultar historial de conversaciones y mensajes",
    description=(
        "Retorna el historial completo de conversaciones y mensajes de chat del prospecto, "
        "ordenados cronológicamente por número de secuencia. Valida pertenencia a la empresa."
    ),
)
def get_lead_conversations(
    lead_id: str,
    company_ctx: CompanyContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> LeadConversationsResponse:
    service = LeadQueryService()
    return service.get_lead_conversations(
        session=db,
        company_id=company_ctx.company_id,
        lead_id=lead_id,
    )


@router.get(
    "/{lead_id}/signals",
    response_model=ConversationAnalysisResponse,
    summary="Consultar señales extraídas y evidencia conversacional",
    description=(
        "Retorna las señales cualitativas extraídas de WhatsApp (intención de compra, "
        "urgencia, solicitud de prueba/cita, manifestación de cuota inicial, modelo) "
        "junto con las citas textuales de evidencia verificable."
    ),
)
def get_lead_signals(
    lead_id: str,
    company_ctx: CompanyContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> ConversationAnalysisResponse:
    service = LeadQueryService()
    return service.get_lead_signals(
        session=db,
        company_id=company_ctx.company_id,
        lead_id=lead_id,
    )


@router.get(
    "/{lead_id}/conversation-analysis",
    response_model=ConversationAnalysisResponse,
    summary="Alias de compatibilidad para señales conversacionales",
    include_in_schema=False,
)
def get_lead_conversation_analysis_alias(
    lead_id: str,
    company_ctx: CompanyContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> ConversationAnalysisResponse:
    service = LeadQueryService()
    return service.get_lead_signals(
        session=db,
        company_id=company_ctx.company_id,
        lead_id=lead_id,
    )


@router.get(
    "/{lead_id}/score",
    response_model=LeadScoreDetail,
    summary="Consultar score, desglose explicable de factores y evidencia",
    description=(
        "Retorna el desglose transparente de la puntuación calculada (0-100), "
        "tier de prioridad, probabilidad de conversión calibrada, ponderación de los "
        "4 factores (conversación, canal histórico, inventario, oportunidad) y "
        "la versión semántica del modelo."
    ),
)
def get_lead_score_detail(
    lead_id: str,
    company_ctx: CompanyContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> LeadScoreDetail:
    service = LeadQueryService()
    return service.get_lead_score(
        session=db,
        company_id=company_ctx.company_id,
        lead_id=lead_id,
    )


@router.post(
    "/prioritize",
    response_model=PrioritizationSummary,
    summary="Disparar cálculo de priorización en lote para la empresa",
    description=(
        "Ejecuta el motor de priorización para todos los prospectos de la empresa "
        "de manera idempotente, actualizando scores y registrando auditoría en scoring_runs."
    ),
)
def trigger_company_prioritization(
    company_ctx: CompanyContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> PrioritizationSummary:
    engine = PrioritizationEngine()
    return engine.prioritize_company_leads(db, company_ctx.company_id)
