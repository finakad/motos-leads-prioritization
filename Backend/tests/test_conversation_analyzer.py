from app.models.conversation import ConversationMessage
from app.services.conversation_analyzer import ConversationAnalyzer


def test_analyzer_high_intent_and_appointment():
    analyzer = ConversationAnalyzer()
    messages = [
        ConversationMessage(
            sequence_number=1,
            sender="cliente",
            text="Buenas tardes, me interesa la Bajaj Pulsar NS 200",
        ),
        ConversationMessage(
            sequence_number=2,
            sender="asesor",
            text="Hola, claro que sí. La tenemos para entrega inmediata.",
        ),
        ConversationMessage(
            sequence_number=3,
            sender="cliente",
            text="Tengo 4 millones de cuota inicial. ¿Puedo agendar una cita mañana para verla?",
        ),
    ]

    res = analyzer.analyze("CONV-TEST-1", messages, "EMP-01", "LD-TEST-1")

    assert res.purchase_intent_score >= 0.70
    assert res.appointment_requested is True
    assert res.down_payment_declared is True
    assert res.model_detected == "Pulsar NS 200"
    assert res.urgency == "alta"

    signals = [e.signal for e in res.evidence]
    assert "cuota_inicial_manifestada" in signals
    assert "solicitud_cita_visita" in signals


def test_analyzer_low_intent_objections():
    analyzer = ConversationAnalyzer()
    messages = [
        ConversationMessage(
            sequence_number=1,
            sender="cliente",
            text="Hola, solo estaba mirando precios, no me interesa comprar ya",
        ),
        ConversationMessage(
            sequence_number=2,
            sender="asesor",
            text="Con gusto, quedamos atentos.",
        ),
        ConversationMessage(
            sequence_number=3,
            sender="cliente",
            text="Estoy mirando otra marca más barata",
        ),
    ]

    res = analyzer.analyze("CONV-TEST-2", messages, "EMP-01", "LD-TEST-2")

    assert res.purchase_intent_score <= 0.40
    assert res.urgency == "baja"
    assert res.signals.has_objections is True
    assert res.appointment_requested is False


def test_analyzer_credit_payment_method():
    analyzer = ConversationAnalyzer()
    messages = [
        ConversationMessage(
            sequence_number=1,
            sender="cliente",
            text="Hola, ¿qué requisitos piden para crédito de la Hero Xpulse 200?",
        ),
        ConversationMessage(
            sequence_number=2,
            sender="asesor",
            text="Buenas tardes, cédula y desprendibles de nómina.",
        ),
        ConversationMessage(
            sequence_number=3,
            sender="cliente",
            text="Perfecto, quiero sacarla financiada a cuotas mensuales.",
        ),
    ]

    res = analyzer.analyze("CONV-TEST-3", messages, "EMP-02", "LD-TEST-3")

    assert res.payment_method == "credito"
    assert res.model_detected == "Xpulse 200"
    assert res.signals.mentions_credit is True
