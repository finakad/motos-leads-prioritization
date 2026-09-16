# Skill: PostgreSQL y persistencia

## Objetivo
Diseñar y evolucionar el esquema relacional manteniendo trazabilidad, integridad y segregación por empresa.

## Principios

- Usar PostgreSQL como base de datos principal.
- Usar SQLAlchemy para modelos y acceso a datos.
- Usar Alembic para migraciones versionadas.
- No modificar el esquema de producción manualmente.
- Toda modificación de modelo persistente debe evaluarse junto con una migración.
- Preferir claves foráneas, restricciones e índices donde correspondan.
- Usar campos de auditoría como `created_at` y `updated_at`.
- Usar `JSONB` solo para estructuras variables, como razones del score o respuesta trazable de IA.
- Mantener las entidades de origen separadas de las entidades consolidadas.

## Validaciones mínimas

- Un lead debe pertenecer a una empresa.
- Un asesor debe pertenecer a una empresa.
- Una asignación diaria debe vincular un lead, un asesor y una fecha.
- La capacidad diaria del asesor debe ser mayor o igual a cero.
- Un resultado de score debe incluir versión y fecha de cálculo.