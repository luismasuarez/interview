# Slack Stock Notifier

Servicio de notificaciones automáticas para Slack que envía dos tipos de mensajes a un canal configurado:

- **Resumen diario de compras** — cada mañana a la hora configurada, lista las compras del día anterior agrupadas por comprador.
- **Alertas de bajo stock** — periódicamente revisa el inventario y notifica si algún producto cae por debajo de su umbral mínimo.

El servicio es de solo lectura: consulta la base de datos pero no modifica ningún dato.

## Mensajes de ejemplo

**Resumen diario:**
```
📊 *Resumen de compras del día - 21/04/2026*

• Ana García: Widget x3, Gadget x1
• Carlos López: Widget x2

Total: 6 unidades
```

**Alerta de stock:**
```
⚠️ *Alerta de bajo stock*

• Widget: 2 unidades (mínimo: 10)
• Gadget: 0 unidades (mínimo: 5)
```

## Requisitos

- [Slack Incoming Webhook URL](https://api.slack.com/messaging/webhooks) (se crea en 2 minutos, sin OAuth)
- Base de datos con las tablas `orders` y `products` (ver [Esquema](#esquema-de-base-de-datos))
- Docker (recomendado) o Python 3.11+

## Inicio rápido con Docker

```bash
# 1. Clonar y configurar
git clone <repo>
cd slack-notifier
cp .env.example .env
# Editar .env con tu SLACK_WEBHOOK_URL

# 2. Levantar
docker compose up -d

# 3. Ver logs
docker compose logs -f
```

## Inicio rápido sin Docker

```bash
# 1. Instalar dependencias
uv pip install -e ".[dev]"   # o: pip install -e ".[dev]"

# 2. Configurar
cp .env.example .env
# Editar .env — cambiar DATABASE_URL a sqlite:///./data.db para desarrollo local

# 3. Ejecutar
python -m slack_notifier.scheduler
```

## Configuración

Todas las opciones se configuran en el archivo `.env` (nunca se almacenan en la imagen):

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SLACK_WEBHOOK_URL` | URL del Incoming Webhook de Slack | `https://hooks.slack.com/services/...` |
| `DATABASE_URL` | Conexión a la base de datos | `sqlite:////app/data/data.db` |
| `DAILY_SUMMARY_HOUR` | Hora del resumen diario (formato 24h) | `8` |
| `DAILY_SUMMARY_MINUTE` | Minuto del resumen diario | `0` |
| `STOCK_CHECK_INTERVAL_MINUTES` | Cada cuántos minutos revisar el stock | `30` |

El servicio falla al arrancar con un mensaje claro si falta alguna variable requerida.

## Esquema de base de datos

El servicio espera estas dos tablas (solo lectura):

```sql
CREATE TABLE products (
    id       INTEGER PRIMARY KEY,
    name     TEXT    NOT NULL,
    stock    INTEGER NOT NULL,
    min_stock INTEGER          -- NULL = excluido de alertas
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    buyer_name  TEXT    NOT NULL,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    order_date  DATE    NOT NULL
);
```

Compatible con SQLite (desarrollo) y PostgreSQL (producción) — solo cambia `DATABASE_URL`.

## Estructura del proyecto

```
slack_notifier/
├── config.py      # Carga y valida variables de entorno
├── db.py          # Consultas a la base de datos
├── slack.py       # Envío de mensajes con reintento automático
├── jobs.py        # Lógica de resumen diario y alerta de stock
└── scheduler.py   # Punto de entrada — inicia el scheduler

tests/
├── unit/          # Tests unitarios (config, jobs, slack)
└── integration/   # Tests de integración (DB en memoria, scheduler)
```

## Tests

```bash
pytest                    # todos los tests (17, 0 fallos)
pytest tests/unit/        # solo unitarios
pytest tests/integration/ # solo integración
```

### Smoke test

Demuestra el funcionamiento end-to-end sin necesidad de Slack ni base de datos externa. Levanta un webhook mock local, crea datos de prueba en memoria y verifica que ambos mensajes se generan con el formato correcto.

**Desde un clone limpio:**

```bash
git clone git@github.com:luismasuarez/interview.git
cd interview
uv venv .venv && uv pip install -e ".[dev]"
.venv/bin/python smoke_test.py
```

Salida esperada:

```
============================================================
SMOKE TEST — Slack Stock Notifier
============================================================

[1/2] daily_summary_job
[2/2] stock_alert_job

── Mensaje 1: Resumen diario ──────────────────────────────
📊 *Resumen de compras del día - 20/04/2026*

• Ana: Gadget x2, Widget x3
• Carlos: Gadget x1

Total: 6 unidades

── Mensaje 2: Alerta de stock ─────────────────────────────
⚠️ *Alerta de bajo stock*

• Widget: 2 unidades (mínimo: 10)

============================================================
✅  SMOKE TEST PASSED — 2/2 mensajes verificados
============================================================
```

## Despliegue en producción

### Con Docker (recomendado)

La imagen está optimizada para producción:
- **72.9 MB** de tamaño final (multi-stage build)
- Proceso corre como usuario no-root (`uid=1001`)
- Imagen base pinada por digest para builds reproducibles
- Configuración 100% por variables de entorno

```bash
docker build -t slack-notifier .
docker run -d --env-file .env --restart unless-stopped slack-notifier
```

### Con systemd

```ini
# /etc/systemd/system/slack-notifier.service
[Unit]
Description=Slack Stock Notifier
After=network.target

[Service]
User=appuser
WorkingDirectory=/opt/slack-notifier
EnvironmentFile=/opt/slack-notifier/.env
ExecStart=/opt/slack-notifier/.venv/bin/python -m slack_notifier.scheduler
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Consideraciones operativas

**Secretos** — El `SLACK_WEBHOOK_URL` es un secreto. Nunca lo incluyas en el repositorio ni en la imagen Docker. En producción usa un gestor de secretos (AWS Secrets Manager, Vault, Docker Secrets) e inyéctalo como variable de entorno en tiempo de ejecución.

**Base de datos** — El servicio es de solo lectura. No necesita permisos de escritura. En PostgreSQL, crea un usuario con `GRANT SELECT` únicamente.

**Zona horaria** — El scheduler usa la zona horaria del sistema. En Docker, pasa `TZ=America/New_York` (o la que corresponda) como variable de entorno para que el resumen diario se envíe a la hora correcta.

**Reintentos** — Si Slack no responde, el servicio reintenta una vez tras 30 segundos. Si el segundo intento falla, registra el error y continúa — no detiene el scheduler.

**Monitoreo** — Todos los eventos se registran en stdout con timestamp. Integra con cualquier sistema de logs que consuma stdout (CloudWatch, Datadog, Loki, etc.). Busca `ERROR` en los logs para detectar fallos de entrega.

**Actualización de la imagen base** — La imagen usa un digest fijo. Cuando salgan parches de seguridad en Python, actualiza el digest en el `Dockerfile` y reconstruye.

## Créditos

Este proyecto fue diseñado e implementado con asistencia de:

- **[Kiro CLI](https://kiro.dev)** — agente de IA que generó el código, los tests y la configuración Docker.
- **[Spec Kit](https://github.com/github/spec-kit)** — toolkit de Spec-Driven Development usado para planificar el proyecto: constitución, especificaciones funcionales, plan técnico y breakdown de tareas antes de escribir una sola línea de código.

## Licencia

MIT
