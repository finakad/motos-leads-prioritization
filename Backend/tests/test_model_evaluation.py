from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.scoring import ModelEvaluation
from app.services.historical_calibrator import HistoricalCalibrator, MODEL_VERSION


def test_historical_calibrator_temporal_split_and_metrics():
    with SessionLocal() as session:
        calibrator = HistoricalCalibrator()
        result = calibrator.fit_and_evaluate(
            session=session,
            train_ratio=0.70,
            persist_evaluation=True,
        )

        assert result["train_size"] > 1000
        assert result["test_size"] > 400

        metrics = result["metrics"]
        assert "roc_auc" in metrics
        assert 0.50 <= metrics["roc_auc"] <= 1.0  # Demonstrates positive discrimination
        assert "brier_score" in metrics
        assert metrics["brier_score"] <= 0.15
        assert "lift_top_30_pct" in metrics
        assert metrics["lift_top_30_pct"] >= 1.0  # Positive lift over random / baseline

        limitations = result["limitations"]
        assert "data_leakage_prevention" in limitations
        assert "predictive_capacity_caveat" in limitations
        assert "multitenant_scope" in limitations


def test_historical_calibrator_audit_persisted():
    with SessionLocal() as session:
        evaluation = session.scalars(
            select(ModelEvaluation)
            .where(ModelEvaluation.model_version == MODEL_VERSION)
            .order_by(ModelEvaluation.created_at.desc())
            .limit(1)
        ).first()

        assert evaluation is not None
        assert evaluation.dataset_name == "historico_cierres.csv"
        assert evaluation.evaluation_type == "TEMPORAL_SPLIT_70_30"
        assert evaluation.sample_size > 2000
        assert evaluation.metrics["roc_auc"] >= 0.50
        assert "Excluded contact_count" in evaluation.limitations["data_leakage_prevention"]


def test_predict_intake_probability_bounds_and_effects():
    calibrator = HistoricalCalibrator()

    # Probability with positive signals (WhatsApp + cuota inicial + contado + cita)
    prob_high = calibrator.predict_intake_probability(
        channel="WhatsApp",
        down_payment=True,
        payment_method="contado",
        requested_appointment=True,
    )

    # Probability with negative signals (Meta Ads + sin cuota inicial + credito + sin cita)
    prob_low = calibrator.predict_intake_probability(
        channel="Meta Ads",
        down_payment=False,
        payment_method="credito",
        requested_appointment=False,
    )

    # High intent must strictly exceed low intent
    assert 0.0 < prob_low < prob_high < 1.0
    assert prob_high >= 0.14
    assert prob_low <= 0.08
