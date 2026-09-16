# Skill: Desarrollo backend

## Objetivo
Implementar funcionalidades del backend siguiendo la arquitectura modular del proyecto.

## Estructura esperada

app/
├── api/
├── core/
├── domain/
├── repositories/
├── services/
├── etl/
├── ai/
├── scoring/
└── main.py

## Responsabilidades

- `api/`: rutas FastAPI, dependencias y esquemas HTTP.
- `core/`: configuración, conexión a base de datos y utilidades transversales.
- `domain/`: entidades, reglas y contratos de negocio.
- `repositories/`: persistencia y consultas a PostgreSQL.
- `services/`: casos de uso y orquestación de reglas de negocio.
- `etl/`: ingesta, validación, normalización y deduplicación.
- `ai/`: contratos, adaptadores y validación de enriquecimiento de conversaciones.
- `scoring/`: cálculo de score, temperatura, explicaciones y validación histórica.

## Criterios de implementación

1. Revisar el requisito funcional relacionado.
2. Identificar entidades, entradas, salidas y reglas.
3. Implementar primero la lógica de dominio.
4. Implementar persistencia mediante repositorio.
5. Implementar servicio o caso de uso.
6. Exponer mediante API solo si el caso de uso requiere consulta o acción externa.
7. Crear pruebas unitarias antes de considerar la funcionalidad terminada.