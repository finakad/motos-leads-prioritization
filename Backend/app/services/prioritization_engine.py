from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.catalog import Motorcycle, MotorcycleAvailability
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.organization import Advisor, SalesPoint
from app.models.scoring import ConversationAnalysis, LeadScore
from app.schemas.scoring import FactorDetail, LeadScoreDetail, PrioritizationSummary
from app.services.conversation_analyzer import ConversationAnalyzer

COLOMBIA_TIMEZONE = ZoneInfo("America/Bogota")
MODEL_VERSION = "v1.0.0"


class PrioritizationEngine:
    """
    Explainable, auditable, multi-tenant lead prioritization engine.
    Computes a composite score (0-100) and priority tier (ALTA/MEDIA/BAJA)
    based on 4 explainable factors with rigorous multi-company isolation.
    """

    def __init__(self, analyzer: ConversationAnalyzer | None = None) -> None:
        self.analyzer = analyzer or ConversationAnalyzer()

    def _evaluate_conversation_factor(
        self,
        session: Session,
        lead: Lead,
    ) -> tuple[float, FactorDetail, list[dict[str, Any]]]:
        """
        Factor 1: Conversation & Intent Analysis (Weight: 35%).
        """
        evidence_items: list[dict[str, Any]] = []

        # Find conversation for this lead
        conversation = session.scalar(
            select(Conversation)
            .where(Conversation.lead_id == lead.id)
            .options(joinedload(Conversation.messages))
        )

        if conversation and conversation.messages:
            # Check or run analysis
            analysis = session.scalar(
                select(ConversationAnalysis).where(
                    ConversationAnalysis.conversation_id == conversation.id
                )
            )
            if analysis is None:
                analysis = self.analyzer.analyze_and_persist(
                    session,
                    conversation.id,
                )

            intent = analysis.purchase_intent_score  # 0.05 to 0.98
            score = round(intent * 35.0, 2)

            factor_ev = [
                f"Intención de compra detectada: {int(intent * 100)}%",
                f"Nivel de urgencia: {analysis.urgency.upper()}",
            ]
            if analysis.appointment_requested:
                factor_ev.append("Cliente solicitó cita / prueba de manejo")
            if analysis.down_payment_declared is True:
                factor_ev.append("Cliente manifestó tener cuota inicial")
            elif analysis.down_payment_declared is False:
                factor_ev.append("Cliente no cuenta con cuota inicial")
            if analysis.payment_method != "no_informa":
                factor_ev.append(f"Forma de pago declarada: {analysis.payment_method}")

            # Collect raw evidence
            for ev in (analysis.evidence or []):
                evidence_items.append(
                    {
                        "source": "conversacion",
                        "sequence": ev.get("sequence_number"),
                        "sender": ev.get("sender"),
                        "text": ev.get("text"),
                        "signal": ev.get("signal"),
                    }
                )

            detail = FactorDetail(
                name="Análisis de Conversación (IA)",
                weight_pct=35.0,
                score_obtained=score,
                max_score=35.0,
                description=(
                    f"Análisis de transcripción WhatsApp ({analysis.urgency.upper()} urgencia, "
                    f"intención {int(intent * 100)}%)."
                ),
                evidence=factor_ev,
            )
            return score, detail, evidence_items

        # No WhatsApp conversation: Neutral fallback
        score = 17.5  # 50% of 35
        factor_ev = ["Lead sin conversación registrada de WhatsApp (canal alternativo)"]
        detail = FactorDetail(
            name="Análisis de Conversación (IA)",
            weight_pct=35.0,
            score_obtained=score,
            max_score=35.0,
            description="Sin conversación de WhatsApp; se asigna puntaje base neutral.",
            evidence=factor_ev,
        )
        return score, detail, evidence_items

    def _evaluate_historical_channel_factor(
        self,
        lead: Lead,
    ) -> tuple[float, FactorDetail]:
        """
        Factor 2: Channel & Historical Conversion (Weight: 25%).
        """
        channel = (lead.channel or "").strip().lower()
        factor_ev: list[str] = []

        if "whatsapp" in channel:
            score = 22.0
            factor_ev.append("Canal WhatsApp: tasa histórica de cierre más alta (9.5%)")
        elif "web" in channel or "formulario" in channel:
            score = 18.0
            factor_ev.append("Canal Formulario Web: tasa histórica de cierre media-alta (9.0%)")
        elif "meta" in channel or "ads" in channel or "facebook" in channel:
            score = 15.0
            factor_ev.append("Canal Meta Ads: tasa histórica de conversión del 8.1%")
        else:
            score = 12.0
            factor_ev.append("Canal sin historial estadístico específico")

        if lead.campaign:
            score = min(25.0, score + 3.0)
            factor_ev.append(f"Campaña de origen activa: '{lead.campaign}'")

        detail = FactorDetail(
            name="Canal y Tasa Histórica",
            weight_pct=25.0,
            score_obtained=round(score, 2),
            max_score=25.0,
            description=f"Evaluación estadística histórica del canal '{lead.channel or 'Desconocido'}'.",
            evidence=factor_ev,
        )
        return round(score, 2), detail

    def _evaluate_inventory_factor(
        self,
        session: Session,
        lead: Lead,
        catalog_models: list[Motorcycle],
        availability_map: set[tuple[str, str]],
    ) -> tuple[float, FactorDetail]:
        """
        Factor 3: Motorcycle Availability & Inventory (Weight: 20%).
        """
        interest_text = (lead.model_interest_text or "").strip().lower()
        factor_ev: list[str] = []

        if not interest_text:
            score = 8.0
            factor_ev.append("Lead no especificó modelo de interés concreto")
            detail = FactorDetail(
                name="Disponibilidad e Inventario",
                weight_pct=20.0,
                score_obtained=score,
                max_score=20.0,
                description="Sin modelo de interés específico en el registro.",
                evidence=factor_ev,
            )
            return score, detail

        # Find best match in catalog
        matched_moto: Motorcycle | None = None
        for m in catalog_models:
            line_clean = m.line.lower()
            brand_clean = m.brand.lower()
            if line_clean in interest_text or interest_text in line_clean:
                matched_moto = m
                break
            if f"{brand_clean} {line_clean}" in interest_text:
                matched_moto = m
                break

        if matched_moto:
            # Check availability in lead's sales point
            has_local_stock = (
                matched_moto.sku,
                lead.sales_point_id,
            ) in availability_map

            if has_local_stock:
                score = 20.0
                factor_ev.append(
                    f"Modelo '{matched_moto.brand} {matched_moto.line}' con inventario "
                    f"confirmado en punto de venta {lead.sales_point_id}."
                )
            elif matched_moto.reported_available_units > 0:
                score = 14.0
                factor_ev.append(
                    f"Modelo '{matched_moto.brand} {matched_moto.line}' disponible en red nacional "
                    f"({matched_moto.reported_available_units} unidades), pero sin stock local."
                )
            else:
                score = 6.0
                factor_ev.append(
                    f"Modelo '{matched_moto.brand} {matched_moto.line}' actualmente sin inventario."
                )
        else:
            score = 10.0
            factor_ev.append(
                f"Modelo cotizado '{lead.model_interest_text}' no identificado exactamente en catálogo oficial."
            )

        detail = FactorDetail(
            name="Disponibilidad e Inventario",
            weight_pct=20.0,
            score_obtained=score,
            max_score=20.0,
            description="Verificación de disponibilidad de stock en catálogo y punto de venta.",
            evidence=factor_ev,
        )
        return score, detail

    def _evaluate_contact_capacity_factor(
        self,
        lead: Lead,
        sales_point_advisors_active: int,
    ) -> tuple[float, FactorDetail]:
        """
        Factor 4: Speed to Contact & Operational Capacity (Weight: 20%).
        """
        factor_ev: list[str] = []

        # If contacted, compute response time in hours
        if lead.registered_at and lead.first_contact_at:
            delta = lead.first_contact_at - lead.registered_at
            hours = max(0.0, delta.total_seconds() / 3600.0)

            if hours <= 2.0:
                score = 20.0
                factor_ev.append(f"Contacto ágil en {hours:.1f} horas (óptimo para conversión)")
            elif hours <= 24.0:
                score = 15.0
                factor_ev.append(f"Contacto realizado en {hours:.1f} horas")
            elif hours <= 72.0:
                score = 10.0
                factor_ev.append(f"Contacto tardío en {hours:.1f} horas")
            else:
                score = 5.0
                factor_ev.append(f"Contacto muy rezagado ({hours:.1f} horas)")
        else:
            # Not yet contacted: fresh lead has high priority opportunity
            score = 16.0
            factor_ev.append("Lead en espera de primer contacto; ventana de oportunidad abierta")

        # Capacity adjustment
        if sales_point_advisors_active > 0:
            factor_ev.append(
                f"Punto de venta {lead.sales_point_id} con {sales_point_advisors_active} asesores activos"
            )
        else:
            score = max(0.0, score - 5.0)
            factor_ev.append(f"Punto de venta {lead.sales_point_id} sin asesores activos registrados")

        detail = FactorDetail(
            name="Oportunidad y Capacidad de Gestión",
            weight_pct=20.0,
            score_obtained=round(score, 2),
            max_score=20.0,
            description="Agilidad en el primer contacto y disponibilidad de asesores para atención.",
            evidence=factor_ev,
        )
        return round(score, 2), detail

    def calculate_lead_score(
        self,
        session: Session,
        lead: Lead,
        catalog_models: list[Motorcycle],
        availability_map: set[tuple[str, str]],
        advisors_count_by_sp: dict[str, int],
    ) -> LeadScoreDetail:
        """Calculates and returns explainable score for a single lead."""

        f1_score, f1_detail, ev1 = self._evaluate_conversation_factor(session, lead)
        f2_score, f2_detail = self._evaluate_historical_channel_factor(lead)
        f3_score, f3_detail = self._evaluate_inventory_factor(
            session, lead, catalog_models, availability_map
        )
        sp_advisors = advisors_count_by_sp.get(lead.sales_point_id, 0)
        f4_score, f4_detail = self._evaluate_contact_capacity_factor(lead, sp_advisors)

        total_score = round(f1_score + f2_score + f3_score + f4_score, 1)
        total_score = max(0.0, min(100.0, total_score))

        if total_score >= 70.0:
            tier = "ALTA"
        elif total_score >= 40.0:
            tier = "MEDIA"
        else:
            tier = "BAJA"

        factors = {
            "conversacion_ia": f1_detail,
            "canal_historico": f2_detail,
            "disponibilidad_inventario": f3_detail,
            "oportunidad_gestion": f4_detail,
        }

        # Add general context evidence
        all_evidence = list(ev1)
        all_evidence.append(
            {
                "source": "perfil_lead",
                "canal": lead.channel,
                "punto_venta": lead.sales_point_id,
                "estado_gestion": lead.management_status,
                "modelo_solicitado": lead.model_interest_text,
            }
        )

        return LeadScoreDetail(
            id=lead.score.id if lead.score else None,  # will be assigned on save
            lead_id=lead.id,
            company_id=lead.company_id,
            sales_point_id=lead.sales_point_id,
            customer_name=lead.customer_name,
            phone_normalized=lead.phone_normalized,
            channel=lead.channel,
            model_interest_text=lead.model_interest_text,
            score=total_score,
            priority_tier=tier,
            factors=factors,
            evidence=all_evidence,
            model_version=MODEL_VERSION,
            calculated_at=datetime.now(timezone.utc),
        )

    def prioritize_company_leads(
        self,
        session: Session,
        company_id: str,
    ) -> PrioritizationSummary:
        """
        Prioritizes all leads belonging strictly to the specified company.
        Guarantees complete multi-tenant segregation.
        """

        # Pre-load reference datasets for efficiency
        catalog_models = list(session.scalars(select(Motorcycle)).all())
        avail_rows = session.execute(
            select(
                MotorcycleAvailability.motorcycle_sku,
                MotorcycleAvailability.sales_point_id,
            )
        ).all()
        availability_map = {(r[0], r[1]) for r in avail_rows}

        # Advisors count by sales point for this company
        advisors = session.scalars(
            select(Advisor).where(
                Advisor.company_id == company_id,
                Advisor.is_active.is_(True),
            )
        ).all()
        advisors_count: dict[str, int] = {}
        for a in advisors:
            advisors_count[a.sales_point_id] = advisors_count.get(a.sales_point_id, 0) + 1

        # Fetch leads strictly belonging to company_id
        leads = list(
            session.scalars(
                select(Lead)
                .where(Lead.company_id == company_id)
                .options(joinedload(Lead.score))
            ).all()
        )

        existing_scores = {
            s.lead_id: s
            for s in session.scalars(
                select(LeadScore).where(LeadScore.company_id == company_id)
            ).all()
        }

        tier_counts = {"ALTA": 0, "MEDIA": 0, "BAJA": 0}
        total_score_sum = 0.0

        for lead in leads:
            score_detail = self.calculate_lead_score(
                session=session,
                lead=lead,
                catalog_models=catalog_models,
                availability_map=availability_map,
                advisors_count_by_sp=advisors_count,
            )

            tier_counts[score_detail.priority_tier] += 1
            total_score_sum += score_detail.score

            factors_dict = {
                k: v.model_dump() for k, v in score_detail.factors.items()
            }

            lead_score = existing_scores.get(lead.id)
            if lead_score is None:
                lead_score = LeadScore(
                    lead_id=lead.id,
                    company_id=company_id,
                    score=score_detail.score,
                    priority_tier=score_detail.priority_tier,
                    factors=factors_dict,
                    evidence=score_detail.evidence,
                    model_version=MODEL_VERSION,
                    calculated_at=score_detail.calculated_at,
                )
                session.add(lead_score)
                existing_scores[lead.id] = lead_score
            else:
                lead_score.score = score_detail.score
                lead_score.priority_tier = score_detail.priority_tier
                lead_score.factors = factors_dict
                lead_score.evidence = score_detail.evidence
                lead_score.model_version = MODEL_VERSION
                lead_score.calculated_at = score_detail.calculated_at

        session.commit()

        avg_score = (
            round(total_score_sum / len(leads), 2) if leads else 0.0
        )

        return PrioritizationSummary(
            company_id=company_id,
            total_leads_evaluated=len(leads),
            scores_calculated=len(leads),
            tier_distribution=tier_counts,
            average_score=avg_score,
            model_version=MODEL_VERSION,
            calculated_at=datetime.now(timezone.utc),
        )
