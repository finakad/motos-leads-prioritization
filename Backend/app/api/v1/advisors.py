from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import CompanyContext, get_company_context
from app.models.organization import Advisor
from app.schemas.advisors import AdvisorResponse

router = APIRouter(
    prefix="/companies/{company_id}/advisors",
    tags=["Advisors & Capacity"],
)


@router.get(
    "",
    response_model=list[AdvisorResponse],
    summary="Listar asesores comerciales por compañía",
    description="Retorna la nómina completa de asesores comerciales y su capacidad diaria para la compañía especificada.",
)
def list_company_advisors(
    company_ctx: CompanyContext = Depends(get_company_context),
    sales_point_id: str | None = Query(None, description="Filtrar por punto de venta"),
    is_active: bool | None = Query(None, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db),
) -> list[Advisor]:
    query = select(Advisor).where(Advisor.company_id == company_ctx.company_id)
    if sales_point_id:
        query = query.where(Advisor.sales_point_id == sales_point_id)
    if is_active is not None:
        query = query.where(Advisor.is_active == is_active)

    query = query.order_by(Advisor.sales_point_id, Advisor.full_name)
    return list(db.scalars(query).all())
