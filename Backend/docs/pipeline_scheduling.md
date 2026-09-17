# Guía de Operación y Programación del Pipeline Backend (Sin Notebooks)

Este documento detalla la configuración, ejecución y despliegue programado del pipeline end-to-end de datos y procesamiento de leads de venta de motocicletas (`motos-leads-prioritization`).

El sistema está diseñado para operar de forma 100% autónoma en backend, sin interacción manual, interfaces gráficas ni notebooks.

---

## 1. Secuencia y Dependencias Explícitas del Pipeline

El flujo de ejecución respeta la siguiente cadena de dependencias topológicas:

```
[1. asesores] -------------> [2. catálogo]
      |                             |
      v                             v
[3. leads] ------------------------>+
      |                             |
      +----------> [4. conversaciones]
      |                   |
      v                   v
[6. deduplicación]   [7. extracción IA]
      |                   |
      +--------+----------+
               |
               v
[5. histórico] +----------> [8. priorización]
```

### Tabla de Pasos

| # | Nombre Paso | Componente Responsable | Salida / Tablas Afectadas | Dependencias Previas |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `advisors` | `load_advisors` | `companies`, `sales_points`, `advisors` | Ninguna |
| **2** | `catalog` | `load_catalog` | `motorcycles`, `motorcycle_availability` | `advisors` |
| **3** | `leads` | `load_leads` | `leads`, `lead_source_records` | `advisors` |
| **4** | `conversations` | `load_conversations` | `conversaciones`, `conversation_messages` | `leads` |
| **5** | `historical_closings` | `load_historical_closings` | `historical_closings` | Ninguna |
| **6** | `deduplication` | `LeadDeduplicationService` | `lead_duplicate_candidates` | `leads` |
| **7** | `conversation_analysis` | `ConversationAnalyzer` | `conversation_analysis` | `conversations` |
| **8** | `prioritization` | `PrioritizationEngine` | `lead_scores`, `scoring_runs` | Pasos 1 a 7 |

---

## 2. Ejecución Manual y Reintento Seguro (CLI)

### 2.1 Ejecución Completa
Para ejecutar todo el pipeline de principio a fin:
```bash
python -m app.etl.runner
```

### 2.2 Reintento desde un Paso Específico (`--from-step`)
Si un paso (por ejemplo, `conversation_analysis`) falló por un problema de conectividad temporal, es posible reanudar la ejecución desde ese paso en adelante sin reiniciar todo el pipeline:
```bash
python -m app.etl.runner --from-step conversation_analysis
```

### 2.3 Ejecución de Pasos Específicos (`--steps`)
Para ejecutar únicamente un subconjunto de pasos seleccionados:
```bash
python -m app.etl.runner --steps deduplication,conversation_analysis,prioritization
```

### 2.4 Listar Pasos Disponibles (`--list-steps`)
```bash
python -m app.etl.runner --list-steps
```

---

## 3. Disparador vía API REST

El pipeline también puede dispararse sincrónicamente vía HTTP a través del endpoint administrativo:

```http
POST /api/v1/etl/trigger
Content-Type: application/json

{
  "from_step": "deduplication",
  "steps": null
}
```

Respuesta esperada:
```json
{
  "run_id": "8fa80243-d48e-4a6c-9ea2-ff1ce7f05809",
  "status": "COMPLETED",
  "message": "Pipeline ETL ejecutado correctamente.",
  "records_processed": 1500,
  "records_rejected": 0
}
```

Para auditar el estado y detalle por pasos de cualquier ejecución:
```http
GET /api/v1/etl/runs/{run_id}
```

---

## 4. Métodos de Despliegue Programado en Producción

### Opción A: Cron en Servidor Linux (VPS / Bare-Metal)

Editar el crontab del usuario de la aplicación (`crontab -e`):

```cron
# Ejecutar cada 2 horas de lunes a sábado
0 */2 * * 1-6 cd /opt/motos-leads-prioritization/Backend && /opt/motos-leads-prioritization/Backend/.venv/bin/python -m app.etl.runner --trigger-type scheduled >> /var/log/motos_pipeline.log 2>&1
```

### Opción B: Systemd Timer (Recomendado en Linux moderno)

1. Crear el archivo de servicio `/etc/systemd/system/motos-leads-pipeline.service`:
```ini
[Unit]
Description=Motos Leads Prioritization Pipeline Runner
After=network.target postgresql.service

[Service]
Type=oneshot
User=appuser
WorkingDirectory=/opt/motos-leads-prioritization/Backend
EnvironmentFile=/opt/motos-leads-prioritization/Backend/.env
ExecStart=/opt/motos-leads-prioritization/Backend/.venv/bin/python -m app.etl.runner --trigger-type systemd_timer
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

2. Crear el temporizador `/etc/systemd/system/motos-leads-pipeline.timer`:
```ini
[Unit]
Description=Timer for Motos Leads Prioritization Pipeline
RefuseManualStart=no
RefuseManualStop=no

[Timer]
# Ejecutar cada hora en punto
OnCalendar=*-*-* *:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

3. Habilitar e iniciar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now motos-leads-pipeline.timer
```

### Opción C: Kubernetes CronJob

En entornos de contenedores (Kubernetes / OpenShift), desplegar un CronJob nativo:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: motos-leads-prioritization-job
  namespace: production
spec:
  schedule: "0 */2 * * *"  # Cada 2 horas
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: pipeline-runner
            image: gcr.io/my-org/motos-backend:latest
            command: ["python", "-m", "app.etl.runner", "--trigger-type", "k8s_cronjob"]
            envFrom:
            - secretRef:
                name: backend-db-secrets
            - configMapRef:
                name: backend-config
```

### Opción D: Cloud Run / Cloud Scheduler (Serverless en GCP)

1. El servicio Backend expone `POST /api/v1/etl/trigger`.
2. Crear un trabajo en Google Cloud Scheduler:
```bash
gcloud scheduler jobs create http motos-leads-hourly-pipeline \
    --schedule="0 * * * *" \
    --uri="https://api.tudominio.com/api/v1/etl/trigger" \
    --http-method=POST \
    --message-body='{"from_step": null}' \
    --oidc-service-account-email="cloud-scheduler-sa@my-project.iam.gserviceaccount.com" \
    --time-zone="America/Bogota"
```

---

## 5. Gestión Segura de Credenciales y Variables de Entorno

**Principio de Cero Credenciales en Código**:
- Ningún comando ni archivo versionado contiene contraseñas, URLs de base de datos ni tokens de API.
- La configuración se resuelve a través de `BaseSettings` (`app/core/config.py`) leyendo variables del sistema o archivo `.env` excluido en `.gitignore`:
  - `DATABASE_URL`: Cadena de conexión cifrada hacia PostgreSQL.
  - `ENVIRONMENT`: Entorno de ejecución (`production`, `staging`, `development`).
  - `APP_LOG_LEVEL`: Nivel de detalle de registro.
