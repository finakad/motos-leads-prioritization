from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class AdvisorResponse(BaseModel):
    """Esquema de respuesta para asesores comerciales con datos operativos."""
    id: str = Field(description="Identificador único del asesor (ej. AS-001)")
    full_name: str = Field(description="Nombre completo del asesor comercial")
    sales_point_id: str = Field(description="Punto de venta o sede asignada")
    company_id: str = Field(description="Compañía a la que pertenece")
    daily_lead_capacity: int = Field(description="Capacidad diaria máxima de atención de leads")
    is_active: bool = Field(description="Indica si el asesor se encuentra activo operativamente")
    hired_at: date = Field(description="Fecha de vinculación a la compañía")

    model_config = ConfigDict(from_attributes=True)
