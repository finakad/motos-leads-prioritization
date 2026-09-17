from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.organization import Company
from app.models.scoring import ConversationAnalysis, LeadScore
from app.schemas.analysis import ConversationAnalysisResponse
from app.schemas.scoring import (
    FactorDetail,
    LeadPrioritizedItem,
    LeadScoreDetail,
    PrioritizationSummary,
)
from app.services.prioritization_engine import PrioritizationEngine

router = APIRouter(
    prefix="/companies/{company_id}/leads",
    tags=["Leads Prioritization"],
)


def _verify_company_exists(session: Session, company_id: str) -> Company:
    company = session.get(Company, company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compañía '{company_id}' no encontrada.",
        )
    return company


@router.get(
    "/prioritized",
    response_model=list[LeadPrioritizedItem],
    summary="List prioritized leads for a company",
)
def list_prioritized_leads(
    company_id: str,
    sales_point_id: str | None = Query(None, description="Filter by sales point ID"),
    priority_tier: Literal["ALTA", "MEDIA", "BAJA"] | None = Query(
        None, description="Filter by priority tier"
    ),
    min_score: float | None = Query(None, ge=0.0, le=100.0, description="Minimum score"),
    limit: int = Query(50, ge=1, le=200, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    db: Session = Depends(get_db),
) -> list[LeadPrioritizedItem]:
    """
    Returns prioritized leads belonging strictly to the company,
    ordered by priority score descending.
    """
    _verify_company_exists(db, company_id)

    query = (
        select(Lead, LeadScore)
        .join(LeadScore, Lead.id == LeadScore.lead_id)
        .where(Lead.company_id == company_id)
        .where(LeadScore.company_id == company_id)
    )

    if sales_point_id:
        query = query.where(Lead.sales_point_id == sales_point_id)

    if priority_tier:
        query = query.where(LeadScore.priority_tier == priority_tier)

    if min_score is not None:
        query = query.where(LeadScore.score >= min_score)

    query = query.order_by(desc(LeadScore.score), Lead.id).limit(limit).offset(offset)

    results = db.execute(query).all()

    # Pre-fetch conversation presence for these leads
    lead_ids = [lead.id for lead, _ in results]
    leads_with_conv = set(
        db.scalars(
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
                phone=lead.phone_normalized or lead.phone_raw,
                channel=lead.channel,
                model_interest=lead.model_interest_text,
                score=score.score,
                priority_tier=score.priority_tier,
                has_conversation=lead.id in leads_with_conv,
                calculated_at=score.calculated_at,
            )
        )

    return items


@router.get(
    "/{lead_id}/score",
    response_model=LeadScoreDetail,
    summary="Get explainable score details and evidence for a lead",
)
def get_lead_score_detail(
    company_id: str,
    lead_id: str,
    db: Session = Depends(get_db),
) -> LeadScoreDetail:
    """
    Returns the comprehensive explainable scoring breakdown, factors,
    and supporting evidence for a single lead, verifying strict tenant isolation.
    """
    _verify_company_exists(db, company_id)

    lead = db.scalar(
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
        # Calculate on the fly if not yet cached
        engine = PrioritizationEngine()
        engine.prioritize_company_leads(db, company_id)
        db.refresh(lead)

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
        phone_normalized=lead.phone_normalized,
        channel=lead.channel,
        model_interest_text=lead.model_interest_text,
        score=score_record.score,
        priority_tier=score_record.priority_tier,
        factors=factors_dict,
        evidence=score_record.evidence,
        model_version=score_record.model_version,
        calculated_at=score_record.calculated_at,
    )


@router.post(
    "/prioritize",
    response_model=PrioritizationSummary,
    summary="Trigger prioritization calculation for all leads of a company",
)
def trigger_company_prioritization(
    company_id: str,
    db: Session = Depends(get_db),
) -> PrioritizationSummary:
    """
    Runs the prioritization engine across all leads of the specified company,
    updating scores and factor breakdowns idempotently.
    """
    _verify_company_exists(db, company_id)
    engine = PrioritizationEngine()
    return engine.prioritize_company_leads(db, company_id)


@router.get(
    "/{lead_id}/conversation-analysis",
    response_model=ConversationAnalysisResponse,
    summary="Get detailed AI conversation analysis for a lead",
)
def get_lead_conversation_analysis(
    company_id: str,
    lead_id: str,
    db: Session = Depends(get_db),
) -> ConversationAnalysisResponse:
    """
    Returns the AI conversation analysis for a lead if a conversation exists.
    """
    _verify_company_exists(db, company_id)

    lead = db.scalar(
        select(Lead).where(Lead.id == lead_id, Lead.company_id == company_id)
    )
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead '{lead_id}' no encontrado en la compañía '{company_id}'.",
        )

    analysis = db.scalar(
        select(ConversationAnalysis).where(
            ConversationAnalysis.lead_id == lead_id,
            ConversationAnalysis.company_id == company_id,
        )
    )

    if analysis is None:
        # Check if conversation exists but unanalyzed
        conv = db.scalar(
            select(Conversation).where(Conversation.lead_id == lead_id)
        )
        if conv is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El lead '{lead_id}' no posee conversaciones de WhatsApp registradas.",
            )

        analyzer = PrioritizationEngine().analyzer
        analysis = analyzer.analyze_and_persist(db, conv.id)

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
