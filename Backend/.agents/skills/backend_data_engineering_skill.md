Habilidad: Ingeniería backend y calidad de datos para Motos Leads Prioritization

Aplica estas prácticas en toda tarea:

1. ETL robusto
   - Validar existencia, codificación UTF-8, columnas requeridas y tipos fuente.
   - Normalizar espacios, textos vacíos, fechas y valores categóricos.
   - Hacer operaciones idempotentes mediante claves de negocio y upsert o actualización controlada.
   - Evitar N+1 queries: precargar referencias necesarias y usar estructuras de búsqueda en memoria cuando aplique.
   - Reportar registros recibidos, procesados y rechazados.
   - Mantener causa y localización de rechazos sin detener la ejecución completa.
   - Mantener el procesamiento dentro de transacciones coherentes, sin abrir transacciones anidadas sobre una sesión ya activa.

2. Integridad y segregación
   - Validar relaciones empresa–punto de venta–asesor–lead.
   - Nunca enlazar entidades de compañías diferentes.
   - Usar claves foráneas, restricciones únicas y checks cuando la regla pertenezca al nivel de base de datos.
   - Validar también en servicios y ETL para producir errores comprensibles.

3. Fechas y zonas horarias
   - Interpretar valores fuente sin zona horaria como America/Bogota.
   - Persistir datetimes timezone-aware.
   - Rechazar fechas imposibles, por ejemplo 2026-08-33.
   - No inventar correcciones para valores de negocio ambiguos o corruptos.

4. IA estructurada
   - Definir un contrato de salida estricto antes de llamar un modelo.
   - Solicitar JSON válido y validarlo con esquemas Pydantic.
   - Guardar entradas relevantes, resultado estructurado, versión de prompt/modelo, estado y fecha de procesamiento.
   - Diseñar el proceso para reintentos seguros e idempotencia.
   - Implementar una estrategia segura de fallback cuando no exista una credencial o proveedor configurado, sin incorporar secretos de ejemplo.

5. Pruebas
   - Cubrir casos válidos, inválidos, nulos, duplicados, reejecución del ETL y cruce de compañías.
   - Usar fixtures aisladas y no depender de archivos locales privados.
   - Incluir al menos una prueba de regresión por cada inconsistencia deliberada descubierta.