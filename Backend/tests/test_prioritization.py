from datetime import datetime, timezone
from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.lead import Lead
from app.models.scoring import LeadScore, ScoringRun
from app.services.prioritization_engine import MODEL_VERSION, PrioritizationEngine


def test_prioritization_engine_calculation():
    with SessionLocal() as session:
        engine = PrioritizationEngine()
        lead = session.scalars(
            select(Lead).where(Lead.company_id == "EMP-01").limit(1)
        ).first()
        assert lead is not None

        # calculate via company prioritization
        summary = engine.prioritize_company_leads(session, "EMP-01")

        assert summary.company_id == "EMP-01"
        assert summary.scores_calculated > 0
        assert summary.average_score > 0.0
        assert summary.model_version == MODEL_VERSION

        # Check persisted score
        score = session.scalar(
            select(LeadScore).where(LeadScore.lead_id == lead.id)
        )
        assert score is not None
        assert 0.0 <= score.score <= 100.0
        assert score.priority_tier in ("ALTA", "MEDIA", "BAJA")
        assert score.conversion_probability is not None
        assert 0.0 <= score.conversion_probability <= 1.0
        assert "conversacion_ia" in score.factors
        assert "canal_historico" in score.factors
        assert "disponibilidad_inventario" in score.factors
        assert "oportunidad_gestion" in score.factors
        assert len(score.evidence) > 0


def test_prioritization_engine_weights_and_tiers():
    with SessionLocal() as session:
        scores = session.scalars(
            select(LeadScore).where(LeadScore.company_id == "EMP-01").limit(20)
        ).all()

        for s in scores:
            f = s.factors
            assert f["conversacion_ia"]["weight_pct"] == 35.0
            assert f["canal_historico"]["weight_pct"] == 25.0
            assert f["disponibilidad_inventario"]["weight_pct"] == 20.0
            assert f["oportunidad_gestion"]["weight_pct"] == 20.0

            if s.score >= 70.0:
                assert s.priority_tier == "ALTA"
            elif s.score >= 40.0:
                assert s.priority_tier == "MEDIA"
            else:
                assert s.priority_tier == "BAJA"


def test_prioritization_multitenant_segregation():
    with SessionLocal() as session:
        engine = PrioritizationEngine()

        # Prioritizing EMP-02 must only touch EMP-02 leads
        summary = engine.prioritize_company_leads(session, "EMP-02")
        assert summary.company_id == "EMP-02"

        # Check all scores generated in this company
        emp2_scores = session.scalars(
            select(LeadScore).where(LeadScore.company_id == "EMP-02")
        ).all()
        assert len(emp2_scores) == summary.scores_calculated

        # Verify no cross-company leads are stored with EMP-02
        for s in emp2_scores:
            lead = session.get(Lead, s.lead_id)
            assert lead is not None
            assert lead.company_id == "EMP-02"


def test_prioritization_idempotency():
    with SessionLocal() as session:
        engine = PrioritizationEngine()

        # Run 1
        summary1 = engine.prioritize_company_leads(session, "EMP-03")
        count1 = session.scalar(
            select(func.count(LeadScore.id)).where(LeadScore.company_id == "EMP-03")
        )

        # Run 2
        summary2 = engine.prioritize_company_leads(session, "EMP-03")
        count2 = session.scalar(
            select(func.count(LeadScore.id)).where(LeadScore.company_id == "EMP-03")
        )

        assert count1 == count2
        assert summary1.scores_calculated == summary2.scores_calculated
        assert summary1.average_score == summary2.average_score


def test_fresh_lead_no_future_variables_leakage():
    with SessionLocal() as session:
        engine = PrioritizationEngine()

        # Fresh uncontacted lead without first_contact_at or conversation
        fresh_lead = Lead(
            id="LEAD-FRESH-TEST",
            company_id="EMP-01",
            sales_point_id="PV-001",
            registered_at=datetime.now(timezone.utc),
            first_contact_at=None,
            channel="WhatsApp",
            customer_name="Persona Test Fresh",
            model_interest_text="Bajaj Pulsar NS 200",
        )

        score_detail = engine.calculate_lead_score(
            session=session,
            lead=fresh_lead,
            catalog_models=[],
            availability_map=set(),
            advisors_count_by_sp={"PV-001": 2},
        )

        assert score_detail is not None
        assert score_detail.score > 0
        # Fresh lead receives opportunity points without error
        opt_factor = score_detail.factors["oportunidad_gestion"]
        assert opt_factor.score_obtained >= 15.0
        assert any("espera de primer contacto" in ev for ev in opt_factor.evidence)


def test_scoring_run_audit_created():
    with SessionLocal() as session:
        engine = PrioritizationEngine()
        engine.prioritize_company_leads(session, "EMP-01")

        run = session.scalars(
            select(ScoringRun)
            .where(ScoringRun.company_id == "EMP-01")
            .order_by(ScoringRun.started_at.desc())
            .limit(1)
        ).first()

        assert run is not None
        assert run.company_id == "EMP-01"
        assert run.model_version == MODEL_VERSION
        assert run.status == "COMPLETED"
        assert run.leads_scored > 0
        assert run.average_score > 0.0
