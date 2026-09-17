from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


def mask_phone(phone: str | None) -> str | None:
    """
    Applies PII data minimization by masking national mobile phone digits.
    Example: '+573104824081' -> '+57 310 *** *081'.
    """
    if not phone:
        return None

    digits = phone.replace("+", "").replace(" ", "").replace("-", "")
    if len(digits) == 12 and digits.startswith("57"):
        # Colombian E.164: +57 3XX XXX XXXX
        country = "+57"
        operator = digits[2:5]
        last_digits = digits[9:]
        return f"{country} {operator} *** *{last_digits}"

    if len(digits) == 10 and digits.startswith("3"):
        operator = digits[:3]
        last_digits = digits[7:]
        return f"+57 {operator} *** *{last_digits}"

    if len(digits) > 4:
        return f"*** *{digits[-4:]}"

    return "****"


class LeadPrioritizedItem(BaseModel):
    """Summarized prioritized lead item with minimized PII."""

    model_config = ConfigDict(from_attributes=True)

    lead_id: str = Field(description="Identificador único del lead")
    company_id: str = Field(description="Compañía propietaria")
    sales_point_id: str = Field(description="Punto de venta asignado")
    customer_name: str | None = Field(None, description="Nombre del prospecto")
    phone_masked: str | None = Field(
        None, description="Teléfono enmascarado para protección de datos"
    )
    channel: str | None = Field(None, description="Canal de adquisición")
    model_interest: str | None = Field(None, description="Motocicleta de interés")
    management_status: str | None = Field(
        None, description="Estado operativo del lead"
    )
    registered_at: datetime | None = Field(
        None, description="Fecha y hora de registro"
    )
    score: float = Field(description="Puntuación compuesta de prioridad (0-100)")
    priority_tier: Literal["ALTA", "MEDIA", "BAJA"] = Field(
        description="Nivel de prioridad operativa"
    )
    conversion_probability: float | None = Field(
        None, description="Probabilidad estadística calibrada de conversión"
    )
    has_conversation: bool = Field(
        False, description="Indica si posee conversaciones de WhatsApp registradas"
    )


class PaginatedLeadsResponse(BaseModel):
    """Paginated envelope for prioritized leads."""

    total: int = Field(description="Total de leads que coinciden con los filtros")
    page: int = Field(description="Página actual (1-indexada)")
    page_size: int = Field(description="Cantidad de elementos por página")
    total_pages: int = Field(description="Total de páginas disponibles")
    items: list[LeadPrioritizedItem] = Field(description="Listado de leads de la página actual")


class LeadDetailResponse(BaseModel):
    """Comprehensive lead details with minimized PII."""

    model_config = ConfigDict(from_attributes=True)

    lead_id: str
    company_id: str
    sales_point_id: str
    customer_name: str | None
    phone_masked: str | None
    channel: str | None
    city: str | None
    model_interest_text: str | None
    management_status: str | None
    registered_at: datetime | None
    first_contact_at: datetime | None
    campaign: str | None
    score: float | None = None
    priority_tier: str | None = None
    conversion_probability: float | None = None
    has_conversation: bool = False


class MessageDetailResponse(BaseModel):
    """Detail of a single chat message."""

    model_config = ConfigDict(from_attributes=True)

    sequence_number: int = Field(description="Orden cronológico del mensaje")
    sender: str = Field(description="Emisor ('cliente', 'asesor', 'sistema')")
    message_time: str | None = Field(None, description="Hora de envío registrada")
    text: str = Field(description="Contenido textual del mensaje")


class ConversationDetailResponse(BaseModel):
    """Conversation thread with ordered message list."""

    model_config = ConfigDict(from_attributes=True)

    conversation_id: str
    channel: str | None
    started_at: datetime | None
    message_count: int
    messages: list[MessageDetailResponse]


class LeadConversationsResponse(BaseModel):
    """Full conversation history for a lead."""

    model_config = ConfigDict(from_attributes=True)

    lead_id: str
    company_id: str
    total_conversations: int
    conversations: list[ConversationDetailResponse]
