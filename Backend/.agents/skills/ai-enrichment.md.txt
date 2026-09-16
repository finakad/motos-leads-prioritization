# Skill: Enriquecimiento de conversaciones con IA

## Objetivo
Extraer información comercial estructurada a partir de conversaciones de WhatsApp.

## Campos de extracción

- motorcycle_model_interest
- down_payment_amount
- payment_method
- declared_intent
- main_objection
- requested_appointment
- requested_quote
- confidence

## Reglas de extracción

- Solicitar salida JSON estructurada.
- Validar la respuesta mediante un esquema Pydantic.
- No inventar datos ausentes.
- Usar `null` cuando la conversación no contenga evidencia suficiente.
- Normalizar el modelo de interés contra el catálogo disponible.
- Guardar fecha de procesamiento, proveedor/modelo utilizado y respuesta trazable.
- Implementar fallback basado en reglas simples para señales como crédito, contado, cita, cotización y montos.
- El proveedor de IA debe estar encapsulado detrás de una interfaz o adaptador.