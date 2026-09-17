from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.deduplication import LeadDuplicateCandidate
from app.models.lead import Lead
from app.models.organization import Company
from app.schemas.deduplication import DeduplicationRunSummary
from app.utils.normalizers import (
    normalize_city,
    normalize_email,
    normalize_model_text,
    normalize_person_name,
    normalize_phone_e164,
    token_similarity,
)


class LeadDeduplicationService:
    """
    Deterministic cross-channel lead deduplication service.
    Strictly enforces multitenant isolation (no cross-company matches).
    Auditable and idempotent persistence without irreversible source mutations.
    """

    def evaluate_pair(
        self,
        lead_a: Lead,
        lead_b: Lead,
    ) -> tuple[str, float, list[str], dict[str, Any]] | None:
        """
        Deterministically evaluates whether two leads are potential duplicates.
        Returns (confidence_tier, match_score, match_reasons, evidence_payload)
        or None if no sufficient match is found.
        """
        # Rule 1: Strict multitenant isolation
        if lead_a.company_id != lead_b.company_id:
            return (
                "NUNCA_COINCIDENCIA",
                0.0,
                ["CROSS_COMPANY_FORBIDDEN"],
                {
                    "company_a": lead_a.company_id,
                    "company_b": lead_b.company_id,
                    "reason": "Matching between different companies is strictly forbidden.",
                },
            )

        if lead_a.id == lead_b.id:
            return None

        # Normalize lead attributes
        phone_a = normalize_phone_e164(lead_a.phone_raw) or lead_a.phone_normalized
        phone_b = normalize_phone_e164(lead_b.phone_raw) or lead_b.phone_normalized

        email_a = normalize_email(lead_a.email)
        email_b = normalize_email(lead_b.email)

        name_a = normalize_person_name(lead_a.customer_name)
        name_b = normalize_person_name(lead_b.customer_name)
        sim = token_similarity(name_a, name_b)

        city_a = normalize_city(lead_a.city)
        city_b = normalize_city(lead_b.city)

        model_a = normalize_model_text(lead_a.model_interest_text)
        model_b = normalize_model_text(lead_b.model_interest_text)

        evidence: dict[str, Any] = {
            "lead_id_a": lead_a.id,
            "lead_id_b": lead_b.id,
            "phone_a": phone_a,
            "phone_b": phone_b,
            "email_a": email_a,
            "email_b": email_b,
            "name_a": lead_a.customer_name,
            "name_b": lead_b.customer_name,
            "name_normalized_a": name_a,
            "name_normalized_b": name_b,
            "name_token_similarity": sim,
            "channel_a": lead_a.channel,
            "channel_b": lead_b.channel,
            "city_a": city_a,
            "city_b": city_b,
            "model_a": model_a,
            "model_b": model_b,
            "registered_at_a": (
                lead_a.registered_at.isoformat()
                if lead_a.registered_at
                else None
            ),
            "registered_at_b": (
                lead_b.registered_at.isoformat()
                if lead_b.registered_at
                else None
            ),
        }

        reasons: list[str] = []

        # High confidence match: Same normalized E.164 phone
        if phone_a and phone_b and phone_a == phone_b:
            reasons.append("SAME_PHONE_E164")
            if email_a and email_b and email_a == email_b:
                reasons.append("SAME_EMAIL")
            if sim >= 0.75:
                reasons.append("SIMILAR_NAME")
            if city_a and city_b and city_a == city_b:
                reasons.append("SAME_CITY")
            if model_a and model_b and model_a == model_b:
                reasons.append("SAME_MODEL")

            score = 1.0 if sim >= 0.7 or not name_a or not name_b else 0.95
            return ("ALTA_CONFIANZA", score, reasons, evidence)

        # High confidence match: Same normalized email
        if email_a and email_b and email_a == email_b:
            reasons.append("SAME_EMAIL")
            if sim >= 0.75:
                reasons.append("SIMILAR_NAME")
            if city_a and city_b and city_a == city_b:
                reasons.append("SAME_CITY")
            if model_a and model_b and model_a == model_b:
                reasons.append("SAME_MODEL")

            score = 1.0 if sim >= 0.7 else 0.95
            return ("ALTA_CONFIANZA", score, reasons, evidence)

        # Possible match: Similar or identical name WITH complementary evidence
        # Negative guard: If both have distinct, valid phones, they are likely homonyms
        if phone_a and phone_b and phone_a != phone_b:
            return None

        # Check name similarity threshold
        name_matched = False
        if sim >= 0.85:
            name_matched = True
        elif name_a and name_b and name_a == name_b and len(name_a.split()) >= 2:
            name_matched = True

        if name_matched:
            signals: list[str] = []
            if city_a and city_b and city_a == city_b:
                signals.append("SAME_CITY")
            if model_a and model_b and model_a == model_b:
                signals.append("SAME_MODEL")
            if (
                lead_a.campaign
                and lead_b.campaign
                and lead_a.campaign.strip().lower()
                == lead_b.campaign.strip().lower()
            ):
                signals.append("SAME_CAMPAIGN")

            if lead_a.registered_at and lead_b.registered_at:
                days_diff = (
                    abs((lead_a.registered_at - lead_b.registered_at).total_seconds())
                    / 86400.0
                )
                if days_diff <= 30.0:
                    signals.append("TEMPORAL_PROXIMITY")

            # Require at least one complementary signal
            if signals:
                reasons.append("SIMILAR_NAME")
                reasons.extend(signals)
                score = round(0.60 + (0.05 * len(signals)) + (0.15 * sim), 4)
                score = min(score, 0.85)
                return ("POSIBLE_COINCIDENCIA", score, reasons, evidence)

        return None

    def detect_duplicates_for_company(
        self,
        session: Session,
        company_id: str,
    ) -> DeduplicationRunSummary:
        """
        Detects duplicate leads for a specific company using blocking indexes.
        Persists candidates idempotently.
        """
        leads = (
            session.scalars(
                select(Lead)
                .where(Lead.company_id == company_id)
                .order_by(Lead.registered_at.asc().nulls_last(), Lead.id.asc())
            )
            .all()
        )

        summary = DeduplicationRunSummary(
            company_id=company_id,
            leads_scanned=len(leads),
        )

        if len(leads) < 2:
            return summary

        # Deterministic Blocking: index by phone, email, and name tokens
        phone_index: dict[str, list[Lead]] = defaultdict(list)
        email_index: dict[str, list[Lead]] = defaultdict(list)
        name_token_index: dict[str, list[Lead]] = defaultdict(list)

        lead_map: dict[str, Lead] = {lead.id: lead for lead in leads}

        for lead in leads:
            phone = normalize_phone_e164(lead.phone_raw) or lead.phone_normalized
            if phone:
                phone_index[phone].append(lead)

            email = normalize_email(lead.email)
            if email:
                email_index[email].append(lead)

            norm_name = normalize_person_name(lead.customer_name)
            if norm_name:
                tokens = [t for t in norm_name.split() if len(t) > 2]
                for token in tokens:
                    name_token_index[token].append(lead)

        # Generate candidate pairs without duplicates
        candidate_pair_keys: set[tuple[str, str]] = set()

        for lead_list in phone_index.values():
            if len(lead_list) > 1:
                for i in range(len(lead_list)):
                    for j in range(i + 1, len(lead_list)):
                        la, lb = lead_list[i], lead_list[j]
                        pair = (la.id, lb.id) if la.id < lb.id else (lb.id, la.id)
                        candidate_pair_keys.add(pair)

        for lead_list in email_index.values():
            if len(lead_list) > 1:
                for i in range(len(lead_list)):
                    for j in range(i + 1, len(lead_list)):
                        la, lb = lead_list[i], lead_list[j]
                        pair = (la.id, lb.id) if la.id < lb.id else (lb.id, la.id)
                        candidate_pair_keys.add(pair)

        for lead_list in name_token_index.values():
            # If a token has too many leads (e.g. generic word), keep block manageable
            if 1 < len(lead_list) <= 50:
                for i in range(len(lead_list)):
                    for j in range(i + 1, len(lead_list)):
                        la, lb = lead_list[i], lead_list[j]
                        pair = (la.id, lb.id) if la.id < lb.id else (lb.id, la.id)
                        candidate_pair_keys.add(pair)

        # Evaluate candidate pairs and persist
        for id_a, id_b in candidate_pair_keys:
            la = lead_map[id_a]
            lb = lead_map[id_b]

            # Primary lead is the older one chronologically
            if la.registered_at and lb.registered_at:
                if la.registered_at <= lb.registered_at:
                    primary, duplicate = la, lb
                else:
                    primary, duplicate = lb, la
            elif la.registered_at:
                primary, duplicate = la, lb
            elif lb.registered_at:
                primary, duplicate = lb, la
            else:
                primary, duplicate = (la, lb) if la.id < lb.id else (lb, la)

            evaluation = self.evaluate_pair(primary, duplicate)
            if not evaluation:
                continue

            tier, score, reasons, evidence = evaluation
            if tier == "NUNCA_COINCIDENCIA":
                continue

            # Check existing candidate
            existing = session.scalar(
                select(LeadDuplicateCandidate).where(
                    LeadDuplicateCandidate.company_id == company_id,
                    LeadDuplicateCandidate.primary_lead_id == primary.id,
                    LeadDuplicateCandidate.duplicate_lead_id == duplicate.id,
                )
            )

            if existing:
                existing.confidence_tier = tier
                existing.match_score = score
                existing.match_reasons = reasons
                existing.evidence_payload = evidence
                existing.updated_at = datetime.now(timezone.utc)
            else:
                candidate = LeadDuplicateCandidate(
                    company_id=company_id,
                    primary_lead_id=primary.id,
                    duplicate_lead_id=duplicate.id,
                    confidence_tier=tier,
                    match_score=score,
                    match_reasons=reasons,
                    evidence_payload=evidence,
                    status="SUGERIDO",
                    decision="PENDIENTE",
                )
                session.add(candidate)

            if tier == "ALTA_CONFIANZA":
                summary.high_confidence_candidates += 1
            elif tier == "POSIBLE_COINCIDENCIA":
                summary.possible_matches += 1

            summary.total_candidates += 1

        if session.in_transaction():
            session.commit()

        return summary

    def detect_all_duplicates(
        self,
        session: Session,
    ) -> list[DeduplicationRunSummary]:
        """
        Executes duplicate detection across all companies independently.
        """
        companies = session.scalars(select(Company.id).order_by(Company.id)).all()
        summaries: list[DeduplicationRunSummary] = []

        for company_id in companies:
            summary = self.detect_duplicates_for_company(session, company_id)
            summaries.append(summary)

        return summaries

    def consolidate_candidate(
        self,
        session: Session,
        candidate_id: UUID,
        decision: str,
        decision_by: str,
        decision_notes: str | None = None,
    ) -> LeadDuplicateCandidate:
        """
        Auditable human or rule-based consolidation.
        Updates candidate decision state without mutating source lead records.
        """
        valid_decisions = {"FUSIONAR_VIRTUAL", "MANTENER_SEPARADOS", "RECHAZADO"}
        if decision not in valid_decisions:
            raise ValueError(
                f"Invalid decision '{decision}'. Must be one of: {valid_decisions}"
            )

        candidate = session.get(LeadDuplicateCandidate, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate '{candidate_id}' not found.")

        candidate.decision = decision
        candidate.decision_by = decision_by
        candidate.decision_notes = decision_notes
        candidate.decided_at = datetime.now(timezone.utc)

        if decision == "FUSIONAR_VIRTUAL":
            candidate.status = "CONSOLIDADO"
        elif decision == "MANTENER_SEPARADOS":
            candidate.status = "CONFIRMADO"
        elif decision == "RECHAZADO":
            candidate.status = "RECHAZADO"

        if session.in_transaction():
            session.commit()

        return candidate


if __name__ == "__main__":
    from app.core.database import SessionLocal

    print("Running cross-channel lead deduplication...")
    with SessionLocal() as db_session:
        service = LeadDeduplicationService()
        results = service.detect_all_duplicates(db_session)
        for r in results:
            print(
                f"Company {r.company_id}: scanned {r.leads_scanned} leads | "
                f"High confidence: {r.high_confidence_candidates} | "
                f"Possible matches: {r.possible_matches} | "
                f"Total candidates: {r.total_candidates}"
            )
