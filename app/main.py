from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, Request, status

from config import get_settings
from schemas import NotifyRequest, NotifyResponse
from security import validate_api_key, verify_meta_signature
from store import NotificationStore
from whatsapp import WhatsAppProviderError, send_whatsapp_text


settings = get_settings()
store = NotificationStore(settings.sqlite_path)

app = FastAPI(title=settings.app_name, version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    store.init_db()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": settings.app_name,
        "env": settings.app_env,
    }


@app.get("/health/live")
def health_live() -> dict[str, Any]:
    return {"ok": True}


@app.get("/health/ready")
def health_ready() -> dict[str, Any]:
    checks = {
        "db": store.is_healthy(),
        "erp_api_key": bool(settings.erp_api_key),
        "whatsapp_verify_token": bool(settings.whatsapp_verify_token),
        "whatsapp_token": bool(settings.whatsapp_token),
        "whatsapp_phone_number_id": bool(settings.whatsapp_phone_number_id),
    }
    ready = all(checks.values())
    return {"ok": ready, "checks": checks}


@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query("", alias="hub.mode"),
    hub_verify_token: str = Query("", alias="hub.verify_token"),
    hub_challenge: str = Query("", alias="hub.challenge"),
) -> str:
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return hub_challenge

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Webhook verification failed",
    )


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> dict[str, Any]:
    raw_body = await request.body()

    if not verify_meta_signature(raw_body, x_hub_signature_256, settings.whatsapp_app_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    store.log_event(event_type="incoming_webhook", payload=payload, status="received")

    return {"status": "received"}


@app.post("/notify", response_model=NotifyResponse)
def notify(
    request_data: NotifyRequest,
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
    x_idempotency_key: str | None = Header(default=None, alias="x-idempotency-key"),
) -> NotifyResponse:
    validate_api_key(x_api_key, settings.erp_api_key)

    if x_idempotency_key:
        previous = store.get_processed_response(x_idempotency_key)
        if previous:
            return NotifyResponse(
                **previous,
                deduplicated=True,
                idempotency_key=x_idempotency_key,
            )

    payload = request_data.model_dump()
    try:
        response = send_whatsapp_text(
            settings=settings,
            telefono=request_data.telefono,
            mensaje=request_data.mensaje,
        )
        message_id = None
        messages = response.get("messages") if isinstance(response, dict) else None
        if isinstance(messages, list) and messages:
            message_id = messages[0].get("id")

        store.log_event(
            event_type="erp_notify",
            payload=payload,
            status="sent",
            phone=request_data.telefono,
        )

        notify_response = NotifyResponse(
            ok=True,
            message_id=message_id,
            provider_response=response,
            deduplicated=False,
            idempotency_key=x_idempotency_key,
        )

        if x_idempotency_key:
            store.save_processed_response(
                x_idempotency_key,
                notify_response.model_dump(),
            )

        return notify_response
    except WhatsAppProviderError as exc:
        store.log_event(
            event_type="erp_notify",
            payload=payload,
            status="error",
            phone=request_data.telefono,
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/notifications/recent")
def notifications_recent(
    limit: int = Query(default=50, ge=1, le=200),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
) -> dict[str, Any]:
    validate_api_key(x_api_key, settings.erp_api_key)
    return {"items": store.list_recent(limit=limit)}
