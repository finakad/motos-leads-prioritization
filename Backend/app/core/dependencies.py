from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.organization import Company


@dataclass(frozen=True)
class CompanyContext:
    """Validated company context for the active request."""

    company_id: str


def get_company_context(
    company_id: str,
    x_company_id: str | None = Header(
        None,
        alias="X-Company-ID",
        description="Opcional: ID de la empresa para verificación cruzada de seguridad.",
    ),
    db: Session = Depends(get_db),
) -> CompanyContext:
    """
    Dependency that resolves and verifies the company context from the route.
    Validates company existence in PostgreSQL and prevents cross-tenant spoofing.
    """
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compañía '{company_id}' no encontrada.",
        )

    # If X-Company-ID header is provided, strictly enforce match
    if x_company_id is not None and x_company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"El encabezado X-Company-ID '{x_company_id}' no coincide con "
                f"la empresa solicitada en la ruta '{company_id}'."
            ),
        )

    return CompanyContext(
        company_id=company.id,
    )

