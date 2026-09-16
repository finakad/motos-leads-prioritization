# Skill: Pipeline de datos

## Objetivo
Procesar de forma automatizada las fuentes de leads, conversaciones, catálogo, asesores e histórico.

## Etapas obligatorias

1. Registrar inicio de ejecución.
2. Validar disponibilidad y estructura de archivos fuente.
3. Cargar datos de origen de forma trazable.
4. Normalizar teléfonos, fechas, ciudades y modelos.
5. Detectar y consolidar duplicados por empresa.
6. Asociar conversaciones con leads cuando exista una relación verificable.
7. Enriquecer conversaciones mediante IA.
8. Calcular score, temperatura y razones de prioridad.
9. Asignar leads por asesor según capacidad diaria.
10. Generar métricas de validación con el histórico.
11. Registrar finalización, resultados y errores de la ejecución.

## Reglas

- Las etapas deben ser idempotentes cuando sea posible.
- No se deben eliminar datos fuente para reemplazarlos por datos transformados.
- Los registros inválidos deben quedar reportados.
- El pipeline debe poder ejecutarse por un único comando.
- Los fallos de una conversación individual no deben invalidar toda la ejecución si el resto de registros puede procesarse.