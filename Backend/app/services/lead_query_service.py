def _normalize_channel(value: str | None) -> str | None:
    if not value:
        return None
    val_clean = value.strip()
    val_lower = val_clean.lower()
    if "whatsapp" in val_lower:
        return "WhatsApp"
    if "meta" in val_lower or "face" in val_lower or "ads" in val_lower:
        return "Meta Ads"
    if "formulario" in val_lower or "web" in val_lower:
        return "Formulario Web"
    return val_clean


from datetime import datetime
import math
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.conversation import Conversation, ConversationMessage
from app.models.lead import Lead
from app.models.organization import Advisor
from app.models.scoring import ConversationAnalysis, LeadScore
from app.schemas.analysis import ConversationAnalysisResponse
from app.schemas.leads import (
    ConversationDetailResponse,
    LeadConversationsResponse,
    LeadDetailResponse,
    LeadPrioritizedItem,
    MessageDetailResponse,
    PaginatedLeadsResponse,
    mask_phone,
)
from app.schemas.scoring import FactorDetail, LeadScoreDetail
from app.services.prioritization_engine import PrioritizationEngine


class LeadQueryService:
    """
    Dedicated service/repository layer for querying leads, scores,
    and conversations with mandatory multi-tenant company segregation.
    """

    def list_prioritized_leads(
        self,
        session: Session,
        company_id: str,
        sales_point_id: str | None = None,
        advisor_id: str | None = None,
        channel: str | None = None,
        status_filter: str | None = None,
        priority_tier: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
        order_by: Literal["score", "registered_at", "customer_name"] = "score",
        order_direction: Literal["asc", "desc"] = "desc",
    ) -> PaginatedLeadsResponse:
        """
        Lists prioritized leads strictly belonging to company_id with
        paginated filtering and deterministic ordering.
        """
        # Base query joining Lead and LeadScore with strict tenant filter
        query = (
            select(Lead, LeadScore)
            .join(LeadScore, Lead.id == LeadScore.lead_id)
            .where(Lead.company_id == company_id)
            .where(LeadScore.company_id == company_id)
        )

        # Sales point filter
        if sales_point_id:
            query = query.where(Lead.sales_point_id == sales_point_id)

        # Advisor filter (resolves advisor to sales point within tenant)
        if advisor_id:
            advisor = session.scalar(
                select(Advisor).where(
                    Advisor.id == advisor_id,
                    Advisor.company_id == company_id,
                )
            )
            if advisor is None:
                # Advisor not found in this company: return empty result safely
                return PaginatedLeadsResponse(
                    total=0,
                    page=page,
                    page_size=page_size,
                    total_pages=0,
                    items=[],
                )
            query = query.where(Lead.sales_point_id == advisor.sales_point_id)

        # Channel filter
        if channel:
            query = query.where(Lead.channel.ilike(f"%{channel.strip()}%"))

        # Management status filter
        if status_filter:
            query = query.where(
                Lead.management_status.ilike(f"%{status_filter.strip()}%")
            )

        # Priority tier filter
        if priority_tier:
            query = query.where(LeadScore.priority_tier == priority_tier.upper())

        # Date range filters
        if date_from:
            query = query.where(Lead.registered_at >= date_from)
        if date_to:
            query = query.where(Lead.registered_at <= date_to)

        # Count total matching records
        count_subquery = select(func.count()).select_from(query.subquery())
        total_count = session.scalar(count_subquery) or 0

        # Sorting
        dir_fn = desc if order_direction == "desc" else asc
        if order_by == "score":
            query = query.order_by(dir_fn(LeadScore.score), Lead.id.asc())
        elif order_by == "registered_at":
            query = query.order_by(dir_fn(Lead.registered_at), Lead.id.asc())
        elif order_by == "customer_name":
            query = query.order_by(dir_fn(Lead.customer_name), Lead.id.asc())
        else:
            query = query.order_by(desc(LeadScore.score), Lead.id.asc())

        # Pagination
        offset = (page - 1) * page_size
        query = query.limit(page_size).offset(offset)

        results = session.execute(query).all()

        lead_ids = [lead.id for lead, _ in results]
        leads_with_conv = set(
            session.scalars(
                select(Conversation.lead_id).where(Conversation.lead_id.in_(lead_ids))
            ).all()
        )

        items: list[LeadPrioritizedItem] = []
        for lead, score in results:
            items.append(
                LeadPrioritizedItem(
                    lead_id=lead.id,
                    company_id=lead.company_id,
                    sales_point_id=lead.sales_point_id,
                    customer_name=lead.customer_name,
                    phone_masked=mask_phone(lead.phone_normalized or lead.phone_raw),
                    channel=_normalize_channel(lead.channel),
                    model_interest=lead.model_interest_text,
                    management_status=lead.management_status,
                    registered_at=lead.registered_at,
                    score=score.score,
                    priority_tier=score.priority_tier,
                    conversion_probability=score.conversion_probability,
                    has_conversation=lead.id in leads_with_conv,
                )
            )

        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

        return PaginatedLeadsResponse(
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=items,
        )

    def get_lead_detail(
        self,
        session: Session,
        company_id: str,
        lead_id: str,
    ) -> LeadDetailResponse:
        """
        Retrieves lead details strictly within the tenant company.
        Applies PII data minimization.
        """
        lead = session.scalar(
            select(Lead)
            .where(Lead.id == lead_id, Lead.company_id == company_id)
            .options(joinedload(Lead.score))
        )

        if lead is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead '{lead_id}' no encontrado en la compañía '{company_id}'.",
            )

        has_conv = (
            session.scalar(
                select(func.count(Conversation.id)).where(
                    Conversation.lead_id == lead_id
                )
            )
            > 0
        )

        return LeadDetailResponse(
            lead_id=lead.id,
            company_id=lead.company_id,
            sales_point_id=lead.sales_point_id,
            customer_name=lead.customer_name,
            phone_masked=mask_phone(lead.phone_normalized or lead.phone_raw),
            channel=_normalize_channel(lead.channel),
            city=lead.city,
            model_interest_text=lead.model_interest_text,
            management_status=lead.management_status,
            registered_at=lead.registered_at,
            first_contact_at=lead.first_contact_at,
            campaign=lead.campaign,
            score=lead.score.score if lead.score else None,
            priority_tier=lead.score.priority_tier if lead.score else None,
            conversion_probability=(
                lead.score.conversion_probability if lead.score else None
            ),
            has_conversation=has_conv,
        )

    def get_lead_conversations(
        self,
        session: Session,
        company_id: str,
        lead_id: str,
    ) -> LeadConversationsResponse:
        """
        Retrieves conversation history and ordered messages for a lead.
        Enforces tenant isolation.
        """
        lead = session.scalar(
            select(Lead.id).where(
                Lead.id == lead_id,
                Lead.company_id == company_id,
            )
        )
        if lead is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead '{lead_id}' no encontrado en la compañía '{company_id}'.",
            )

        conversations = session.scalars(
            select(Conversation)
            .where(Conversation.lead_id == lead_id)
            .order_by(Conversation.started_at.asc().nulls_last())
        ).all()

        conv_details: list[ConversationDetailResponse] = []
        for conv in conversations:
            messages = session.scalars(
                select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conv.id)
                .order_by(ConversationMessage.sequence_number.asc())
            ).all()

            msg_details = [
                MessageDetailResponse(
                    sequence_number=m.sequence_number,
                    sender=m.sender,
                    message_time=str(m.message_time) if m.message_time is not None else None,
                    text=m.text,
                )
                for m in messages
            ]

            conv_details.append(
                ConversationDetailResponse(
                    conversation_id=conv.id,
                    channel=conv.channel,
                    started_at=conv.started_at,
                    message_count=len(messages),
                    messages=msg_details,
                )
            )

        return LeadConversationsResponse(
            lead_id=lead_id,
            company_id=company_id,
            total_conversations=len(conv_details),
            conversations=conv_details,
        )

    def get_lead_signals(
        self,
        session: Session,
        company_id: str,
        lead_id: str,
    ) -> ConversationAnalysisResponse:
        """
        Retrieves AI conversation signals and verifiable evidence for a lead.
        """
        lead = session.scalar(
            select(Lead.id).where(
                Lead.id == lead_id,
                Lead.company_id == company_id,
            )
        )
        if lead is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead '{lead_id}' no encontrado en la compañía '{company_id}'.",
            )

        analysis = session.scalar(
            select(ConversationAnalysis).where(
                ConversationAnalysis.lead_id == lead_id,
                ConversationAnalysis.company_id == company_id,
            )
        )

        if analysis is None:
            # Check if conversation exists
            conv = session.scalar(
                select(Conversation).where(Conversation.lead_id == lead_id)
            )
            if conv is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El lead '{lead_id}' no posee conversaciones de WhatsApp registradas.",
                )

            analyzer = PrioritizationEngine().analyzer
            analysis = analyzer.analyze_and_persist(session, conv.id)

        return ConversationAnalysisResponse(
            id=analysis.id,
            conversation_id=analysis.conversation_id,
            lead_id=analysis.lead_id,
            company_id=analysis.company_id,
            purchase_intent_score=analysis.purchase_intent_score,
            urgency=analysis.urgency,
            down_payment_declared=analysis.down_payment_declared,
            payment_method=analysis.payment_method,
            appointment_requested=analysis.appointment_requested,
            model_detected=analysis.model_detected,
            signals=analysis.signals,
            evidence=analysis.evidence,
            analyzed_at=analysis.analyzed_at,
        )

    def get_lead_score(
        self,
        session: Session,
        company_id: str,
        lead_id: str,
    ) -> LeadScoreDetail:
        """
        Retrieves explainable score details, factors, and supporting evidence.
        """
        lead = session.scalar(
            select(Lead)
            .where(Lead.id == lead_id, Lead.company_id == company_id)
            .options(joinedload(Lead.score))
        )

        if lead is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead '{lead_id}' no encontrado en la compañía '{company_id}'.",
            )

        if lead.score is None:
            engine = PrioritizationEngine()
            engine.prioritize_company_leads(session, company_id)
            session.refresh(lead)

        score_record = lead.score
        if score_record is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al recuperar el score del lead.",
            )

        factors_dict = {
            name: FactorDetail(**data)
            for name, data in score_record.factors.items()
        }

        return LeadScoreDetail(
            id=score_record.id,
            lead_id=lead.id,
            company_id=lead.company_id,
            sales_point_id=lead.sales_point_id,
            customer_name=lead.customer_name,
            phone_normalized=mask_phone(lead.phone_normalized or lead.phone_raw),
            channel=_normalize_channel(lead.channel),
            model_interest_text=lead.model_interest_text,
            score=score_record.score,
            priority_tier=score_record.priority_tier,
            conversion_probability=score_record.conversion_probability,
            factors=factors_dict,
            evidence=score_record.evidence,
            model_version=score_record.model_version,
            calculated_at=score_record.calculated_at,
        )
