import re
import unicodedata
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, ConversationMessage
from app.models.lead import Lead
from app.models.scoring import ConversationAnalysis
from app.schemas.analysis import (
    ConversationAnalysisResult,
    ConversationSignals,
    EvidenceItem,
)

COLOMBIA_TIMEZONE = ZoneInfo("America/Bogota")


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "MN"
    )


class ConversationAnalyzer:
    """
    Verifiable and deterministic conversation intelligence analyzer.
    Extracts structured intent, urgency, down payment, payment method,
    appointment requests, and motorcycle interest with verifiable textual evidence.
    """

    # Down payment patterns
    RE_DOWN_PAYMENT_POS = re.compile(
        r"(tengo|doy|con|aporto|dispongo|dar[eé]|cuento con)\s+.*(cuota\s*inicial|inicial|mill[oó]n|palos|\$?\d+[\d\.]*)|"
        r"(cuota\s*inicial\s*de|inicial\s*de\s*\$?\d+)|"
        r"tengo\s+(\$?\d+[\d\.]*|\d+\s*(millones?|mil))\s*(para\s*la\s*inicial|de\s*inicial)?",
        re.IGNORECASE,
    )
    RE_DOWN_PAYMENT_NEG = re.compile(
        r"(no\s*tengo|sin|cero)\s*(plata\s*para\s*)?(cuota\s*inicial|inicial|dinero|plata)|"
        r"sin\s*inicial",
        re.IGNORECASE,
    )

    # Payment method patterns
    RE_CASH = re.compile(
        r"\b(contado|en\s*efectivo|de\s*una|transferencia|plata\s*en\s*mano|pago\s*completo)\b",
        re.IGNORECASE,
    )
    RE_CREDIT = re.compile(
        r"\b(cr[eé]dito|financiad[ao]|financiar|a\s*cuotas|cuotas\s*mensuales|papeleo|requisitos\s*del\s*cr[eé]dito)\b",
        re.IGNORECASE,
    )

    # Appointment / visit patterns
    RE_APPOINTMENT = re.compile(
        r"(cita|visita|acercarme|pasar\s*(por|al|a\s*la)|agendar|separar|"
        r"puedo\s*ir|ir\s*a\s*verla|verla\s*en\s*persona|prueba\s*de\s*manejo|test\s*drive)",
        re.IGNORECASE,
    )

    # Urgency patterns
    RE_URGENCY_HIGH = re.compile(
        r"(esta\s*semana|inmediat[ao]|lo\s*antes\s*posible|urgente|urge|ya\s*mismo|"
        r"para\s*ya|la\s*necesito\s*ya|cu[aá]nto\s*demora\s*la\s*entrega|hoy\s*mismo|ma[nñ]ana)",
        re.IGNORECASE,
    )

    # Low intent / objections
    RE_LOW_INTENT = re.compile(
        r"(solo\s*estaba\s*mirando|solo\s*mirando|curioseando|mirando\s*precios|"
        r"otra\s*marca|muy\s*cara|no\s*me\s*alcanza|despu[eé]s\s*les\s*aviso|"
        r"no\s*me\s*interesa|no\s*gracias|por\s*ahora\s*no)",
        re.IGNORECASE,
    )

    # Common Colombian motorcycle models / line identifiers
    KNOWN_MODELS = [
        "Pulsar RS 200",
        "Pulsar NS 200",
        "Pulsar NS 160",
        "Pulsar",
        "Xpulse 200",
        "Xpulse",
        "NKD 125",
        "NKD",
        "Dio 110",
        "Dio",
        "Hunk 160R",
        "Hunk",
        "XR 150L",
        "XR 190L",
        "V-Strom 250",
        "V-Strom",
        "Discover 125",
        "Discover",
        "Boxer CT 100",
        "Boxer",
        "TTR 200",
        "TTR",
        "Dynamic Pro 125",
        "Dynamic",
        "NMax 155",
        "NMax",
        "FZ 25",
        "FZ-S",
        "FZ",
        "Gixxer 150",
        "Gixxer 250",
        "Gixxer",
        "Dash 110",
        "Best 125",
        "DR 150",
        "Apache RTR 200",
        "Apache RTR 160",
        "Apache",
    ]

    def analyze(
        self,
        conversation_id: str,
        messages: list[ConversationMessage],
        company_id: str,
        lead_id: str | None = None,
    ) -> ConversationAnalysisResult:
        """Analyzes all messages in a conversation and extracts verifiable signals."""

        evidence: list[EvidenceItem] = []
        client_msgs = [m for m in messages if m.sender.lower() == "cliente"]
        advisor_msgs = [m for m in messages if m.sender.lower() == "asesor"]

        total_count = len(messages)
        client_count = len(client_msgs)
        ratio = (client_count / total_count) if total_count > 0 else 0.0

        mentions_down_payment_pos = False
        mentions_down_payment_neg = False
        mentions_cash = False
        mentions_credit = False
        mentions_visit = False
        urgency_high = False
        has_objections = False
        model_detected: str | None = None

        # Inspect all client messages chronologically
        for msg in client_msgs:
            text = msg.text
            clean = _strip_accents(text)

            # Check down payment
            if self.RE_DOWN_PAYMENT_POS.search(text) or self.RE_DOWN_PAYMENT_POS.search(clean):
                mentions_down_payment_pos = True
                evidence.append(
                    EvidenceItem(
                        sequence_number=msg.sequence_number,
                        sender="cliente",
                        text=text,
                        signal="cuota_inicial_manifestada",
                        confidence=0.95,
                    )
                )

            if self.RE_DOWN_PAYMENT_NEG.search(text) or self.RE_DOWN_PAYMENT_NEG.search(clean):
                mentions_down_payment_neg = True
                evidence.append(
                    EvidenceItem(
                        sequence_number=msg.sequence_number,
                        sender="cliente",
                        text=text,
                        signal="sin_cuota_inicial",
                        confidence=0.90,
                    )
                )

            # Check payment method
            if self.RE_CASH.search(text) or self.RE_CASH.search(clean):
                mentions_cash = True
                evidence.append(
                    EvidenceItem(
                        sequence_number=msg.sequence_number,
                        sender="cliente",
                        text=text,
                        signal="forma_pago_contado",
                        confidence=0.95,
                    )
                )

            if self.RE_CREDIT.search(text) or self.RE_CREDIT.search(clean):
                mentions_credit = True
                evidence.append(
                    EvidenceItem(
                        sequence_number=msg.sequence_number,
                        sender="cliente",
                        text=text,
                        signal="forma_pago_credito",
                        confidence=0.95,
                    )
                )

            # Check appointment / visit
            if self.RE_APPOINTMENT.search(text) or self.RE_APPOINTMENT.search(clean):
                mentions_visit = True
                evidence.append(
                    EvidenceItem(
                        sequence_number=msg.sequence_number,
                        sender="cliente",
                        text=text,
                        signal="solicitud_cita_visita",
                        confidence=0.95,
                    )
                )

            # Check high urgency
            if self.RE_URGENCY_HIGH.search(text) or self.RE_URGENCY_HIGH.search(clean):
                urgency_high = True
                evidence.append(
                    EvidenceItem(
                        sequence_number=msg.sequence_number,
                        sender="cliente",
                        text=text,
                        signal="alta_urgencia",
                        confidence=0.90,
                    )
                )

            # Check objections / low intent
            if self.RE_LOW_INTENT.search(text) or self.RE_LOW_INTENT.search(clean):
                has_objections = True
                evidence.append(
                    EvidenceItem(
                        sequence_number=msg.sequence_number,
                        sender="cliente",
                        text=text,
                        signal="objecion_bajo_interes",
                        confidence=0.85,
                    )
                )

            # Check motorcycle model mention
            if model_detected is None:
                for km in self.KNOWN_MODELS:
                    if re.search(r"\b" + re.escape(km) + r"\b", text, re.IGNORECASE):
                        model_detected = km
                        evidence.append(
                            EvidenceItem(
                                sequence_number=msg.sequence_number,
                                sender="cliente",
                                text=text,
                                signal=f"modelo_mencionado:{km}",
                                confidence=0.95,
                            )
                        )
                        break

        # If model not in client text, check first advisor message if client quoted it implicitly
        if model_detected is None and messages:
            first_msg = messages[0].text
            for km in self.KNOWN_MODELS:
                if re.search(r"\b" + re.escape(km) + r"\b", first_msg, re.IGNORECASE):
                    model_detected = km
                    break

        # Compute structured fields
        if mentions_down_payment_pos:
            down_payment_declared = True
        elif mentions_down_payment_neg:
            down_payment_declared = False
        else:
            down_payment_declared = None

        if mentions_cash and not mentions_credit:
            payment_method = "contado"
        elif mentions_credit and not mentions_cash:
            payment_method = "credito"
        elif mentions_cash and mentions_credit:
            payment_method = "credito"  # usually mixed implies looking at financing
        else:
            payment_method = "no_informa"

        appointment_requested = mentions_visit

        # Compute purchase intent score (0.0 to 1.0)
        score = 0.35  # base interaction

        if client_count >= 3:
            score += 0.10
        elif client_count == 1:
            score -= 0.05

        if model_detected is not None:
            score += 0.15

        if mentions_visit:
            score += 0.25

        if down_payment_declared is True:
            score += 0.15
        elif down_payment_declared is False:
            score -= 0.10

        if payment_method == "contado":
            score += 0.10
        elif payment_method == "credito":
            score += 0.05

        if urgency_high:
            score += 0.10

        if has_objections:
            score -= 0.30

        # Clamp score between 0.05 and 0.98
        final_score = round(max(0.05, min(0.98, score)), 4)

        # Urgency
        if urgency_high or (mentions_visit and final_score >= 0.70):
            urgency = "alta"
        elif final_score >= 0.45 or mentions_credit:
            urgency = "media"
        else:
            urgency = "baja"

        signals = ConversationSignals(
            client_message_count=client_count,
            client_engagement_ratio=round(ratio, 3),
            mentions_down_payment=bool(mentions_down_payment_pos or mentions_down_payment_neg),
            mentions_credit=mentions_credit,
            mentions_cash=mentions_cash,
            mentions_visit_or_test_drive=mentions_visit,
            has_objections=has_objections,
            model_detected=model_detected,
        )

        return ConversationAnalysisResult(
            conversation_id=conversation_id,
            lead_id=lead_id,
            company_id=company_id,
            purchase_intent_score=final_score,
            urgency=urgency,
            down_payment_declared=down_payment_declared,
            payment_method=payment_method,
            appointment_requested=appointment_requested,
            model_detected=model_detected,
            signals=signals,
            evidence=evidence,
        )

    def analyze_and_persist(
        self,
        session: Session,
        conversation_id: str,
    ) -> ConversationAnalysis:
        """Analyzes a conversation from database and persists the analysis record."""

        conversation = session.get(Conversation, conversation_id)
        if conversation is None:
            raise ValueError(f"Conversation '{conversation_id}' not found.")

        # Determine company_id from matched lead or default
        company_id = "EMP-01"
        if conversation.lead_id:
            lead = session.get(Lead, conversation.lead_id)
            if lead:
                company_id = lead.company_id

        messages = conversation.messages
        result = self.analyze(
            conversation_id=conversation.id,
            messages=messages,
            company_id=company_id,
            lead_id=conversation.lead_id,
        )

        analysis = session.scalar(
            select(ConversationAnalysis).where(
                ConversationAnalysis.conversation_id == conversation.id
            )
        )

        evidence_payload = [e.model_dump() for e in result.evidence]
        signals_payload = result.signals.model_dump()

        if analysis is None:
            analysis = ConversationAnalysis(
                conversation_id=result.conversation_id,
                lead_id=result.lead_id,
                company_id=result.company_id,
                purchase_intent_score=result.purchase_intent_score,
                urgency=result.urgency,
                down_payment_declared=result.down_payment_declared,
                payment_method=result.payment_method,
                appointment_requested=result.appointment_requested,
                model_detected=result.model_detected,
                signals=signals_payload,
                evidence=evidence_payload,
            )
            session.add(analysis)
        else:
            analysis.lead_id = result.lead_id
            analysis.company_id = result.company_id
            analysis.purchase_intent_score = result.purchase_intent_score
            analysis.urgency = result.urgency
            analysis.down_payment_declared = result.down_payment_declared
            analysis.payment_method = result.payment_method
            analysis.appointment_requested = result.appointment_requested
            analysis.model_detected = result.model_detected
            analysis.signals = signals_payload
            analysis.evidence = evidence_payload

        session.flush()
        return analysis
