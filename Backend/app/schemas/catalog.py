from pydantic import BaseModel, ConfigDict, Field


class MotorcycleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str = Field(..., description="Código SKU único de la motocicleta")
    brand: str = Field(..., description="Marca del fabricante (ej. Honda, Yamaha)")
    line: str = Field(..., description="Línea o modelo comercial (ej. CB 125F Twister)")
    engine_displacement_cc: int = Field(
        ..., description="Cilindraje en centímetros cúbicos (cc)"
    )
    segment: str = Field(
        ..., description="Segmento de mercado (ej. Trabajo, Scooter, Deportiva)"
    )
    list_price: int = Field(..., description="Precio de lista oficial en COP")
    reported_available_units: int = Field(
        ..., description="Unidades reportadas en inventario"
    )
    available_sales_points: list[str] = Field(
        default_factory=list,
        description="Listado de sedes/puntos de venta de la compañía donde hay disponibilidad",
    )


class MotorcycleListResponse(BaseModel):
    items: list[MotorcycleResponse]
    total: int = Field(..., description="Total de modelos que cumplen los filtros")
    brands: list[str] = Field(
        default_factory=list, description="Lista de marcas disponibles en el catálogo"
    )
    segments: list[str] = Field(
        default_factory=list, description="Lista de segmentos disponibles en el catálogo"
    )
