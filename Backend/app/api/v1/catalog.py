from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import CompanyContext, get_company_context
from app.models.catalog import Motorcycle, MotorcycleAvailability
from app.models.organization import SalesPoint
from app.schemas.catalog import MotorcycleListResponse, MotorcycleResponse

router = APIRouter(
    prefix="/companies/{company_id}/catalog",
    tags=["Catalog & Inventory"],
)


@router.get(
    "/motorcycles",
    response_model=MotorcycleListResponse,
    summary="Listar motocicletas del catálogo con disponibilidad por empresa",
    description=(
        "Retorna el catálogo de motocicletas con filtros por marca, segmento, "
        "rango de precio, punto de venta y búsqueda libre. Incluye las sedes de la compañía "
        "donde cada modelo tiene disponibilidad registrada."
    ),
)
def list_company_motorcycles(
    company_ctx: CompanyContext = Depends(get_company_context),
    sales_point_id: str | None = Query(
        None, description="Filtrar por punto de venta específico de la compañía"
    ),
    brand: str | None = Query(None, description="Filtrar por marca (ej. Honda, Yamaha)"),
    segment: str | None = Query(
        None, description="Filtrar por segmento (ej. Trabajo, Scooter, Deportiva)"
    ),
    search: str | None = Query(
        None, description="Búsqueda por texto en línea, marca o SKU"
    ),
    min_price: int | None = Query(None, ge=0, description="Precio mínimo de lista en COP"),
    max_price: int | None = Query(None, ge=0, description="Precio máximo de lista en COP"),
    db: Session = Depends(get_db),
) -> MotorcycleListResponse:
    # 1. Obtener puntos de venta autorizados para la compañía
    company_sales_points = list(
        db.scalars(
            select(SalesPoint.id).where(SalesPoint.company_id == company_ctx.company_id)
        ).all()
    )

    # Si se especificó un punto de venta, validar que pertenezca a la compañía
    if sales_point_id:
        if sales_point_id not in company_sales_points:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Punto de venta '{sales_point_id}' no pertenece a la compañía '{company_ctx.company_id}'.",
            )

    # 2. Construir consulta de motocicletas
    query = select(Motorcycle)

    if brand:
        query = query.where(func.lower(Motorcycle.brand) == brand.strip().lower())

    if segment:
        query = query.where(func.lower(Motorcycle.segment) == segment.strip().lower())

    if min_price is not None:
        query = query.where(Motorcycle.list_price >= min_price)

    if max_price is not None:
        query = query.where(Motorcycle.list_price <= max_price)

    if search and search.strip():
        pattern = f"%{search.strip().lower()}%"
        query = query.where(
            or_(
                func.lower(Motorcycle.line).like(pattern),
                func.lower(Motorcycle.brand).like(pattern),
                func.lower(Motorcycle.sku).like(pattern),
                func.lower(Motorcycle.segment).like(pattern),
            )
        )

    if sales_point_id:
        query = query.join(
            MotorcycleAvailability,
            Motorcycle.sku == MotorcycleAvailability.motorcycle_sku,
        ).where(MotorcycleAvailability.sales_point_id == sales_point_id)

    query = query.order_by(Motorcycle.brand, Motorcycle.line)
    motorcycles = list(db.scalars(query).all())

    # 3. Mapear disponibilidad por sede para las motocicletas seleccionadas
    skus = [m.sku for m in motorcycles]
    availability_map: dict[str, list[str]] = {sku: [] for sku in skus}

    if skus and company_sales_points:
        avail_query = (
            select(
                MotorcycleAvailability.motorcycle_sku,
                MotorcycleAvailability.sales_point_id,
            )
            .where(
                MotorcycleAvailability.motorcycle_sku.in_(skus),
                MotorcycleAvailability.sales_point_id.in_(company_sales_points),
            )
            .order_by(MotorcycleAvailability.sales_point_id)
        )

        for sku, sp_id in db.execute(avail_query):
            availability_map[sku].append(sp_id)

    # 4. Obtener listas maestras de marcas y segmentos para filtros
    all_brands = sorted(list(db.scalars(select(distinct(Motorcycle.brand))).all()))
    all_segments = sorted(list(db.scalars(select(distinct(Motorcycle.segment))).all()))

    items = [
        MotorcycleResponse(
            sku=m.sku,
            brand=m.brand,
            line=m.line,
            engine_displacement_cc=m.engine_displacement_cc,
            segment=m.segment,
            list_price=m.list_price,
            reported_available_units=m.reported_available_units,
            available_sales_points=availability_map.get(m.sku, []),
        )
        for m in motorcycles
    ]

    return MotorcycleListResponse(
        items=items,
        total=len(items),
        brands=all_brands,
        segments=all_segments,
    )


@router.get(
    "/motorcycles/{sku}",
    response_model=MotorcycleResponse,
    summary="Obtener detalle técnico y disponibilidad de una motocicleta por SKU",
    description="Retorna la información completa del modelo y las sedes de la compañía donde hay stock.",
)
def get_motorcycle_by_sku(
    sku: str,
    company_ctx: CompanyContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> MotorcycleResponse:
    motorcycle = db.scalar(
        select(Motorcycle).where(func.lower(Motorcycle.sku) == sku.strip().lower())
    )
    if not motorcycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Motocicleta con SKU '{sku}' no encontrada en el catálogo.",
        )

    company_sales_points = list(
        db.scalars(
            select(SalesPoint.id).where(SalesPoint.company_id == company_ctx.company_id)
        ).all()
    )

    available_sps: list[str] = []
    if company_sales_points:
        available_sps = list(
            db.scalars(
                select(MotorcycleAvailability.sales_point_id)
                .where(
                    MotorcycleAvailability.motorcycle_sku == motorcycle.sku,
                    MotorcycleAvailability.sales_point_id.in_(company_sales_points),
                )
                .order_by(MotorcycleAvailability.sales_point_id)
            ).all()
        )

    return MotorcycleResponse(
        sku=motorcycle.sku,
        brand=motorcycle.brand,
        line=motorcycle.line,
        engine_displacement_cc=motorcycle.engine_displacement_cc,
        segment=motorcycle.segment,
        list_price=motorcycle.list_price,
        reported_available_units=motorcycle.reported_available_units,
        available_sales_points=available_sps,
    )
