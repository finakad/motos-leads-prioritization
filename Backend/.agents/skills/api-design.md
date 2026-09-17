# Skill: Diseño de API

## Objetivo
Exponer una API REST clara, validada y segregada por empresa.

## Endpoints iniciales esperados

- `GET /health`
- `GET /api/advisors/{advisor_id}/daily-leads`
- `GET /api/leads/{lead_id}`
- `GET /api/metrics/priority-validation`

## Reglas

- Usar Pydantic para request y response models.
- Retornar códigos HTTP consistentes.
- No exponer entidades internas de base de datos directamente.
- Aplicar el contexto de empresa en cada consulta.
- Paginar colecciones cuando el volumen lo requiera.
- Documentar automáticamente los endpoints en FastAPI.
- Retornar mensajes de error comprensibles sin revelar información sensible.