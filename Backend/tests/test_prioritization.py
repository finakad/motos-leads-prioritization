from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.lead import Lead
from app.models.scoring import LeadScore
from app.services.prioritization_engine import PrioritizationEngine


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
        assert summary.model_version == "v1.0.0"

        # Check persisted score
        score = session.scalar(
            select(LeadScore).where(LeadScore.lead_id == lead.id)
        )
        assert score is not None
        assert 0.0 <= score.score <= 100.0
        assert score.priority_tier in ("ALTA", "MEDIA", "BAJA")
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
