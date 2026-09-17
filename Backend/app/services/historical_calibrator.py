from collections import defaultdict
from datetime import datetime, timezone
import math
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.history import HistoricalClosing
from app.models.scoring import ModelEvaluation


MODEL_VERSION = "v1.2.0-calibrated"
DATASET_NAME = "historico_cierres.csv"


class HistoricalCalibrator:
    """
    Calibrates empirical conversion weights and evaluates predictive performance
    using a chronological split on historical closings without data leakage.
    """

    def __init__(self) -> None:
        self.base_conversion_rate: float = 0.0975
        self.base_log_odds: float = math.log(0.0975 / (1.0 - 0.0975))
        self.channel_weights: dict[str, float] = {}
        self.down_payment_weights: dict[str, float] = {}
        self.payment_method_weights: dict[str, float] = {}
        self.appointment_weights: dict[bool, float] = {}
        self.is_fitted: bool = False

    def fit_and_evaluate(
        self,
        session: Session,
        train_ratio: float = 0.70,
        persist_evaluation: bool = True,
    ) -> dict[str, Any]:
        """
        Fits on the first train_ratio (chronological 70%) and evaluates
        on the remaining test_ratio (chronological 30%).
        Persists metrics and limitations to model_evaluations table.
        """
        rows = (
            session.scalars(
                select(HistoricalClosing)
                .where(HistoricalClosing.target_converted.isnot(None))
                .order_by(
                    HistoricalClosing.registered_at.asc(),
                    HistoricalClosing.id.asc(),
                )
            )
            .all()
        )

        if not rows:
            raise RuntimeError("No historical closings found with target_converted.")

        split_idx = int(len(rows) * train_ratio)
        train_rows = rows[:split_idx]
        test_rows = rows[split_idx:]

        train_pos = sum(1 for r in train_rows if r.target_converted is True)
        self.base_conversion_rate = train_pos / len(train_rows)
        self.base_log_odds = math.log(
            self.base_conversion_rate / (1.0 - self.base_conversion_rate)
        )

        # Helper to compute Laplace-smoothed log odds ratio
        def compute_effects(feat_extractor) -> dict[Any, float]:
            counts = defaultdict(lambda: {"total": 0, "pos": 0})
            for r in train_rows:
                k = feat_extractor(r)
                counts[k]["total"] += 1
                if r.target_converted is True:
                    counts[k]["pos"] += 1

            weights = {}
            m = 10.0  # Smoothing prior weight
            for k, c in counts.items():
                p_smoothed = (c["pos"] + m * self.base_conversion_rate) / (
                    c["total"] + m
                )
                log_odds = math.log(p_smoothed / (1.0 - p_smoothed))
                weights[k] = log_odds - self.base_log_odds
            return weights

        self.channel_weights = compute_effects(
            lambda r: (r.channel or "").strip().lower()
        )
        self.down_payment_weights = compute_effects(
            lambda r: (r.down_payment_manifested or "NO_INFORMA").strip().upper()
        )
        self.payment_method_weights = compute_effects(
            lambda r: (r.declared_payment_method or "no_informa").strip().lower()
        )
        self.appointment_weights = compute_effects(
            lambda r: bool(r.requested_appointment)
        )
        self.is_fitted = True

        # Evaluate on held-out temporal test set
        y_true: list[int] = [
            1 if r.target_converted is True else 0 for r in test_rows
        ]
        y_pred: list[float] = [
            self.predict_intake_probability(
                channel=r.channel,
                down_payment=self._parse_down_payment_bool(r.down_payment_manifested),
                payment_method=r.declared_payment_method,
                requested_appointment=bool(r.requested_appointment),
            )
            for r in test_rows
        ]

        test_actual_rate = sum(y_true) / len(y_true)
        avg_pred_prob = sum(y_pred) / len(y_pred)

        # Brier score
        brier = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred)) / len(y_true)
        brier_baseline = sum(
            (yt - self.base_conversion_rate) ** 2 for yt in y_true
        ) / len(y_true)

        # ROC-AUC via Mann-Whitney U
        pos_preds = [p for yt, p in zip(y_true, y_pred) if yt == 1]
        neg_preds = [p for yt, p in zip(y_true, y_pred) if yt == 0]
        u = 0.0
        for p in pos_preds:
            for n in neg_preds:
                if p > n:
                    u += 1.0
                elif p == n:
                    u += 0.5
        roc_auc = (
            u / (len(pos_preds) * len(neg_preds))
            if (len(pos_preds) * len(neg_preds)) > 0
            else 0.5
        )

        # Lift in Top 30% prioritized leads
        sorted_pairs = sorted(zip(y_pred, y_true), key=lambda x: -x[0])
        top_k = int(len(sorted_pairs) * 0.30)
        top_slice = sorted_pairs[:top_k]
        top_conversion = (
            sum(yt for _, yt in top_slice) / len(top_slice) if top_slice else 0.0
        )
        lift_top_30 = (
            top_conversion / test_actual_rate if test_actual_rate > 0 else 1.0
        )

        metrics = {
            "roc_auc": round(roc_auc, 4),
            "brier_score": round(brier, 4),
            "baseline_brier_score": round(brier_baseline, 4),
            "train_actual_conversion": round(self.base_conversion_rate, 4),
            "test_actual_conversion": round(test_actual_rate, 4),
            "average_predicted_prob": round(avg_pred_prob, 4),
            "top_30_pct_conversion": round(top_conversion, 4),
            "lift_top_30_pct": round(lift_top_30, 2),
        }

        limitations = {
            "data_leakage_prevention": (
                "Excluded contact_count and post-hoc hours_to_first_contact to prevent "
                "temporal target leakage during lead intake scoring."
            ),
            "predictive_capacity_caveat": (
                f"With purely intake variables, model achieves ROC-AUC {round(roc_auc, 4)} "
                f"and {round(lift_top_30, 2)}x lift in top 30%. Conversion is strongly determined "
                "by conversational intent and downstream advisor engagement, not initial channel alone."
            ),
            "multitenant_scope": (
                "Model weights reflect global consumer behavior across 3 companies; operational "
                "scoring strictly isolates leads, inventory, and advisor availability per tenant."
            ),
        }

        if persist_evaluation:
            evaluation = ModelEvaluation(
                model_version=MODEL_VERSION,
                dataset_name=DATASET_NAME,
                evaluation_type="TEMPORAL_SPLIT_70_30",
                sample_size=len(rows),
                train_size=len(train_rows),
                test_size=len(test_rows),
                metrics=metrics,
                limitations=limitations,
                created_at=datetime.now(timezone.utc),
            )
            session.add(evaluation)
            if session.in_transaction():
                session.commit()

        return {
            "metrics": metrics,
            "limitations": limitations,
            "train_size": len(train_rows),
            "test_size": len(test_rows),
        }

    def _parse_down_payment_bool(self, val: str | None) -> bool | None:
        if not val:
            return None
        v = str(val).strip().upper()
        if v == "SI" or v == "TRUE":
            return True
        if v == "NO" or v == "FALSE":
            return False
        return None

    def predict_intake_probability(
        self,
        channel: str | None,
        down_payment: bool | None,
        payment_method: str | None,
        requested_appointment: bool = False,
    ) -> float:
        """
        Calculates calibrated conversion probability based on intake features.
        """
        z = self.base_log_odds

        ch = (channel or "").strip().lower()
        if "whatsapp" in ch:
            z += self.channel_weights.get("whatsapp", 0.07)
        elif "web" in ch or "formulario" in ch:
            z += self.channel_weights.get("formulario web", -0.01)
        elif "meta" in ch or "ads" in ch or "facebook" in ch:
            z += self.channel_weights.get("meta ads", -0.12)

        if down_payment is True:
            z += self.down_payment_weights.get("SI", 0.20)
        elif down_payment is False:
            z += self.down_payment_weights.get("NO", -0.11)
        else:
            z += self.down_payment_weights.get("NO_INFORMA", -0.18)

        pm = (payment_method or "no_informa").strip().lower()
        if pm in self.payment_method_weights:
            z += self.payment_method_weights[pm]

        if requested_appointment:
            z += self.appointment_weights.get(True, 0.18)
        else:
            z += self.appointment_weights.get(False, -0.08)

        # Sigmoid
        prob = 1.0 / (1.0 + math.exp(-z))
        return round(prob, 4)
