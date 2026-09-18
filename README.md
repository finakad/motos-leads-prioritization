# Sistema de Priorización y Gestión Inteligente de Leads de Motocicletas

Solución integral de analítica predictiva, priorización comercial y gestión operativa de prospectos (leads), con arquitectura multi-tenant estricta, explicabilidad de decisiones y pipeline ETL automatizado.

---

## Enlaces Públicos de la Solución

- **Aplicación Web (Frontend en Producción):** [https://motos-leads.up.railway.app/](https://motos-leads.up.railway.app/)
- **Documentación Interactiva del Backend (Swagger / OpenAPI):** [https://motos-leads-prioritization-production.up.railway.app/docs#/](https://motos-leads-prioritization-production.up.railway.app/docs#/)

---

## 1. ¿Qué Hace el Sistema?

El sistema resuelve el desafío comercial de concesionarios que reciben cientos de prospectos diarios por múltiples canales (WhatsApp, Formularios Web, Meta Ads), optimizando el tiempo de los asesores mediante:

1. **Ingesta y Procesamiento Automatizado (ETL Idempotente):**
   - Carga y normaliza catálogos de motocicletas, sedes, asesores con su capacidad diaria, prospectos operativos y más de 15.000 registros históricos de cierres.
2. **Deduplicación Explicable y Consolidación de Prospectos:**
   - Detección determinista de prospectos duplicados entre canales según reglas auditables: alta confianza (teléfono E.164 normalizado o correo electrónico dentro de la misma empresa) y posible coincidencia (nombre normalizado con señales complementarias), garantizando la no mezcla entre compañías distintas.
3. **Extracción de Señales Comerciales con IA:**
   - Análisis de conversaciones omnicanal para identificar intención real de compra, urgencia, modelo de motocicleta de interés, sensibilidad a precio, método de pago (crédito vs. contado) y objeciones frecuentes.
4. **Motor de Priorización Explicable y Calibrado:**
   - Asignación de un puntaje continuo (Score 0-100) y estratificación en niveles de prioridad (**ALTA**, **MEDIA**, **BAJA**), fundamentado en patrones empíricos del histórico de cierres de ventas.
   - Generación de explicabilidad transparente: factores que impulsan la compra, señales de riesgo y recomendaciones de acción inmediata para el asesor comercial.
5. **Aislamiento Multitenant Estricto:**
   - Segregación total entre empresas (`EMP-01`, `EMP-02`, `EMP-03`). Ningún usuario o consulta puede acceder o filtrar datos de una compañía ajena.
6. **Plataforma Web Reactiva y moderna:**
   - Dashboard analítico con KPIs comerciales, distribuciones de cartera y prospectos urgentes.
   - Gestión operativa de leads con filtros dinámicos, paginación y minimización de datos (PII enmascarado).
   - Ficha detallada de cada prospecto con historial de conversaciones, señales IA y desglose del score.
   - Catálogo interactivo de motocicletas con especificaciones técnicas, precios oficiales en COP y disponibilidad de inventario por sede.
   - Monitoreo de asesores y capacidad operativa instalada.

---

## 2. Arquitectura de la Solución

```
motos-leads-prioritization/
├── Backend/                       # API REST en FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── api/v1/                # Routers: leads, catalog, advisors, etl
│   │   ├── core/                  # Configuración, base de datos, dependencias de tenant
│   │   ├── etl/                   # Pipeline runner, loaders y scripts de migración
│   │   ├── models/                # Modelos declarativos SQLAlchemy (multitenant)
│   │   ├── schemas/               # Esquemas de validación Pydantic
│   │   ├── services/              # Motores: priorización, deduplicación, análisis IA
│   │   └── utils/                 # Normalizadores (E.164, texto, nombres)
│   ├── tests/                     # Suite de pruebas automatizadas con pytest
│   ├── alembic/                   # Control de versiones de base de datos
│   ├── Dockerfile                 # Contenedor de producción para Backend
│   └── requirements.txt
│
├── Frontend/                      # SPA React 19 + TypeScript + Vite + TailwindCSS
│   ├── src/
│   │   ├── app/                   # Enrutamiento y proveedores de estado (React Query)
│   │   ├── components/            # Componentes UI reutilizables y layout responsivo
│   │   ├── config/                # Entorno y navegación
│   │   ├── features/              # Módulos de dominio:
│   │   │   ├── leads/             # Gestión de prospectos y detalle operativo
│   │   │   ├── dashboard/         # Métricas, KPIs y distribuciones
│   │   │   ├── catalog/           # Catálogo y fichas técnicas de motocicletas
│   │   │   └── advisors/          # Capacidad de asesores
│   │   └── pages/                 # Pantallas de la aplicación
│   ├── Dockerfile                 # Contenedor de producción con NGINX
│   └── package.json
└── README.md
```

---

## 3. ¿Cómo se Ejecuta Localmente?

### Prerrequisitos
- **Python:** Versión 3.11 o superior.
- **Node.js:** Versión 18 o superior con `npm`.
- **PostgreSQL:** Base de datos activa (local o mediante contenedor Docker).

---

### A. Configuración y Ejecución del Backend

1. **Navegar a la carpeta Backend:**
   ```bash
   cd Backend
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Copie el archivo de ejemplo y defina las variables de conexión a su base de datos:
   ```bash
   cp .env.example .env
   ```
   *Configuración en `.env`:*
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/motos_leads_db
   ALLOWED_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ENVIRONMENT=development
   ```

5. **Aplicar migraciones de base de datos:**
   ```bash
   alembic upgrade head
   ```

6. **Ejecutar el pipeline de datos (ETL completo):**
   ```bash
   python -m app.etl.runner
   ```

7. **Iniciar el servidor backend (FastAPI):**
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   *La documentación interactiva estará disponible en:* `http://127.0.0.1:8000/docs`

8. **Ejecutar la suite de pruebas automatizadas:**
   ```bash
   pytest
   ```

---

### B. Configuración y Ejecución del Frontend

1. **Navegar a la carpeta Frontend:**
   ```bash
   cd Frontend
   ```

2. **Instalar dependencias:**
   ```bash
   npm install
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   ```
   *Variables configurables en `.env`:*
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   VITE_DATA_SOURCE=api
   VITE_DEFAULT_COMPANY_ID=EMP-01
   ```
   *(Para ejecutar en modo offline demostrativo sin backend local, use `VITE_DATA_SOURCE=mock`).*

4. **Iniciar el servidor de desarrollo:**
   ```bash
   npm run dev
   ```
   *La aplicación estará disponible en:* `http://localhost:5173/`

5. **Verificación de calidad de código y compilación:**
   ```bash
   # Verificación de tipos TypeScript
   npm run typecheck

   # Análisis estático y linter
   npm run lint

   # Generación del bundle de producción
   npm run build
   ```

---

## 4. Decisiones Técnicas Tomadas

1. **Aislamiento Multi-Empresa Estricto (Tenant Isolation):**
   - Toda consulta operativa exige resolver la empresa mediante ruta (`/companies/{company_id}/...`) y header de verificación (`X-Company-ID`). Si se intenta consultar un recurso o sede que no pertenece a la compañía en contexto, el backend rechaza la solicitud retornando `HTTP 404`, previniendo fugas de información entre empresas competidoras.
2. **Minimización de Datos Personales (Privacy by Design):**
   - En cumplimiento de buenas prácticas de protección de datos personales, los teléfonos y datos sensibles nunca se exponen en texto plano en la API ni en pantalla: se transforman a formatos enmascarados (ej. `+57 310 *** 8921`), restringiendo el dato crudo exclusivamente a la base de datos interna.
3. **Motor de Priorización Basado en Evidencia Histórica:**
   - En lugar de recurrir a modelos de caja negra no auditables, se implementó un motor calibrado contra la tasa de conversión empírica de 15.000 cierres históricos, combinando factores multiplicativos por canal, método de pago, intención conversacional y tipo de motocicleta, acompañado siempre de razones explicables y recomendaciones.
4. **Arquitectura Desacoplada y Dual en Frontend:**
   - La capa de presentación consume servicios tipados (`IDashboardService`, `ILeadsService`, `ICatalogService`, `IAdvisorsService`) con esquemas Zod. Cada módulo cuenta con una implementación API y una implementación Mock local, garantizando robustez y facilidad de prueba en entornos desconectados.
5. **Dashboard Derivable con Transparencia de Censo:**
   - Dado que FastAPI no exponía un endpoint agregador rígido para el dashboard, las métricas se derivan en el cliente a partir del censo real y auditado de prospectos, informando al usuario mediante un banner explícito sobre la fuente y cantidad de registros procesados.

---

## 5. Supuestos Asumidos

1. **Contexto de Autenticación de Compañía:**
   - Se asume que el contexto de la empresa solicitante es resuelto por la infraestructura de seguridad mediante cabeceras o parámetros de ruta validados por middleware, permitiendo conmutar entre compañías (`EMP-01`, `EMP-02`, `EMP-03`) para efectos de auditoría y demostración comercial.
2. **Moneda y Parámetros Comerciales:**
   - Todos los valores monetarios corresponden a pesos colombianos (COP).
   - Los números telefónicos siguen el estándar internacional E.164 (+57 para números móviles en Colombia).
3. **Modelo de Extracción IA:**
   - Las conversaciones se analizan mediante un motor modular que admite integración con proveedores de LLM o un extractor heurístico determinista de alta precisión para ejecución local offline y pruebas CI/CD.
4. **Capacidad Operativa de Asesores:**
   - La capacidad máxima de atención diaria por asesor se toma como un límite suave; los prospectos con prioridad ALTA tienen prelación en la asignación sobre la cola de espera general.

---

## 6. ¿Qué Haría con Más Tiempo?

1. **Autenticación Robusta y Control de Acceso Basado en Roles (RBAC):**
   - Implementación de OpenID Connect / OAuth2 con tokens JWT cifrados, diferenciando permisos entre *Asesor de Ventas* (solo ve sus prospectos asignados), *Líder de Sede* (ve su punto de venta) y *Gerente General* (consolida métricas de su compañía).
2. **Notificaciones y Asignación en Tiempo Real (WebSockets / SSE):**
   - Transmisión instantánea de eventos hacia la interfaz de usuario cuando ingrese un prospecto calificado con prioridad ALTA, permitiendo contacto en menos de 5 minutos (ventana dorada de conversión).
3. **Pipeline MLOps y Reentrenamiento Continuo:**
   - Automatización del ciclo de vida del modelo mediante tracking de experimentos (MLflow), re-calibración mensual automática contra nuevos cierres reales y monitoreo de deriva de datos (*data drift*).
4. **Integración Bidireccional de Canales de Mensajería:**
   - Conexión directa con la API oficial de WhatsApp Business Cloud para enviar plantillas pre-aprobadas y gestionar la conversación directamente desde la ficha del prospecto en la plataforma.
5. **Pruebas End-to-End Automatizadas:**
   - Implementación de suite de pruebas completas con Playwright para validar flujos de usuario críticos (búsqueda, filtrado, visualización de fichas y navegación) ejecutadas en el pipeline de Integración Continua (CI/CD).
