# Asuna WhatsApp Bot (Python)

Servicio FastAPI para conectar tu ERP con WhatsApp Cloud API.

## Que incluye

- `GET /webhook`: verificacion de Meta
- `POST /webhook`: recepcion de eventos de WhatsApp
- `POST /notify`: envio de mensajes desde tu ERP
- `POST /notify/template`: envio de plantillas aprobadas desde tu ERP
- `GET /notifications/recent`: consulta de logs recientes
- `GET /health/live`: liveness probe
- `GET /health/ready`: readiness probe con validaciones de configuracion
- Seguridad por `x-api-key` para endpoints internos
- Segmentacion por app usando `x-app-id` (ej: `farmacia`, `gimnasio`, `rrhh`)
- Verificacion de firma `X-Hub-Signature-256` en webhook (si configuras `WHATSAPP_APP_SECRET`)
- Idempotencia por `x-idempotency-key` para evitar envios duplicados
- Logs en SQLite (`notifications.db`)

## Arquitectura por carpetas

```text
app/
  api/
    dependencies.py
    routes/
      health.py
      legal.py
      notifications.py
      webhook.py
  core/
    config.py
    container.py
    security.py
  integrations/
    whatsapp_provider.py
  models/
    schemas.py
  repositories/
    notification_store.py
  main.py
```

Los archivos de raiz (`config.py`, `security.py`, `schemas.py`, `store.py`, `whatsapp.py`) se mantienen como wrappers de compatibilidad para no romper imports existentes.

## Requisitos

- Python 3.10+
- Cuenta de Meta Developers con WhatsApp Cloud API habilitado

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` con tus credenciales reales.

## Ejecutar

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Configurar webhook en Meta

En el panel de tu app (WhatsApp):

1. URL del callback: `https://TU_DOMINIO/webhook`
2. Verify token: el mismo valor de `WHATSAPP_VERIFY_TOKEN`
3. Suscribe al menos `messages` y `message_status`.

## Multi-app (farmacia, gimnasio, rrhh)

Puedes usar el mismo bot para varias apps separando por `x-app-id` y una API key por app.

Variables recomendadas:

- `DEFAULT_APP_ID=farmacia`
- `ERP_API_KEYS=farmacia:claveFarmacia,gimnasio:claveGym,rrhh:claveRRHH`

Con eso, cada app solo ve sus propios logs en `GET /notifications/recent` y su idempotencia queda aislada por app.

## Probar envio desde ERP

```bash
curl -X POST "http://localhost:8000/notify" \
  -H "Content-Type: application/json" \
  -H "x-app-id: farmacia" \
  -H "x-api-key: pon-una-clave-segura" \
  -H "x-idempotency-key: venta-123-factura" \
  -d '{"telefono":"51987654321","mensaje":"Tu venta V-20260317-0004 fue facturada"}'
```

Si reenvias la misma solicitud con el mismo `x-idempotency-key`, el servicio devolvera la respuesta anterior sin enviar un mensaje duplicado.

## Probar envio con plantilla

Usa este endpoint cuando quieras iniciar conversaciones fuera de la ventana de 24 horas.

```bash
curl -X POST "http://localhost:8000/notify/template" \
  -H "Content-Type: application/json" \
  -H "x-app-id: farmacia" \
  -H "x-api-key: pon-una-clave-segura" \
  -H "x-idempotency-key: venta-123-template" \
  -d '{
    "telefono":"51987654321",
    "template_name":"venta_confirmada",
    "language_code":"es_PE",
    "components":[
      {"type":"body","parameters":["Juan","V-20260317-0004","16.52"]}
    ]
  }'
```

Ejemplo de plantilla sugerida en Meta:

- Nombre: `venta_confirmada`
- Categoria: `UTILITY`
- Texto del body: `Hola {{1}}, tu compra {{2}} por S/ {{3}} fue registrada correctamente.`

El valor de `language_code` debe coincidir exactamente con el idioma aprobado en Meta para esa plantilla. Si la traduccion aprobada es `es`, no funcionara enviar `es_PE`.

## Integracion sugerida con tu ERP

- Evento `VENTA_COMPLETADA`
- Evento `COMPRA_RECIBIDA`
- Evento `FACTURA_EMITIDA`

Cada evento llama `POST /notify` con telefono y mensaje final para el cliente.

## Endpoints

- `GET /health`
- `GET /health/live`
- `GET /health/ready`
- `GET /privacy-policy`
- `GET /data-deletion`
- `GET /webhook`
- `POST /webhook`
- `POST /notify`
- `POST /notify/template`
- `GET /notifications/recent`

## Produccion con Docker

```bash
copy .env.example .env
docker compose up -d --build
```

Salud de despliegue:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

## Produccion en Render

Este repo ya incluye `render.yaml` en la raiz (`Asuna/render.yaml`) para deploy automatico.

1. Sube el repo a GitHub.
2. En Render: `New +` -> `Blueprint` y selecciona tu repo.
3. Render detectara `render.yaml` y creara el servicio `asuna-whatsapp-bot`.
4. En `Environment` completa los secretos:
  - `DEFAULT_APP_ID`
  - `ERP_API_KEYS` (recomendado para multi-app)
  - `ERP_API_KEY` (opcional, solo modo simple de una sola app)
  - `WHATSAPP_TOKEN`
  - `WHATSAPP_PHONE_NUMBER_ID`
  - `WHATSAPP_VERIFY_TOKEN`
  - `WHATSAPP_APP_SECRET`
5. Espera el deploy y valida:
  - `https://TU-SERVICIO.onrender.com/health/live`
  - `https://TU-SERVICIO.onrender.com/health/ready`

Webhook en Meta:

- URL de callback: `https://TU-SERVICIO.onrender.com/webhook`
- Verify token: el mismo valor de `WHATSAPP_VERIFY_TOKEN`
