from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from api.dependencies import resolve_app_id
from core.container import settings, store
from integrations.whatsapp_provider import (
    WhatsAppProviderError,
    send_whatsapp_template,
    send_whatsapp_text,
)
from models.schemas import NotifyRequest, NotifyResponse, TemplateNotifyRequest

router = APIRouter(tags=["notifications"])


def _build_request_key(app_id: str, idempotency_key: str) -> str:
    return f"{app_id}:{idempotency_key}"


@router.post("/notify", response_model=NotifyResponse)
def notify(
    request_data: NotifyRequest,
    x_idempotency_key: str | None = Header(default=None, alias="x-idempotency-key"),
    app_id: str = Depends(resolve_app_id),
) -> NotifyResponse:
    if x_idempotency_key:
        request_key = _build_request_key(app_id, x_idempotency_key)
        previous = store.get_processed_response(request_key)
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
            app_id=app_id,
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
                request_key,
                notify_response.model_dump(),
                app_id,
            )

        return notify_response
    except WhatsAppProviderError as exc:
        store.log_event(
            app_id=app_id,
            event_type="erp_notify",
            payload=payload,
            status="error",
            phone=request_data.telefono,
            error_message=str(exc),
        )
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.post("/notify/template", response_model=NotifyResponse)
def notify_template(
    request_data: TemplateNotifyRequest,
    x_idempotency_key: str | None = Header(default=None, alias="x-idempotency-key"),
    app_id: str = Depends(resolve_app_id),
) -> NotifyResponse:
    if x_idempotency_key:
        request_key = _build_request_key(app_id, x_idempotency_key)
        previous = store.get_processed_response(request_key)
        if previous:
            return NotifyResponse(
                **previous,
                deduplicated=True,
                idempotency_key=x_idempotency_key,
            )

    payload = request_data.model_dump()
    components = [
        {
            "type": component.type,
            "parameters": [
                {"type": "text", "text": value}
                for value in component.parameters
            ],
        }
        for component in request_data.components
        if component.parameters
    ]

    try:
        response = send_whatsapp_template(
            settings=settings,
            telefono=request_data.telefono,
            template_name=request_data.template_name,
            language_code=request_data.language_code,
            components=components,
        )
        message_id = None
        messages = response.get("messages") if isinstance(response, dict) else None
        if isinstance(messages, list) and messages:
            message_id = messages[0].get("id")

        store.log_event(
            app_id=app_id,
            event_type="erp_notify_template",
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
                request_key,
                notify_response.model_dump(),
                app_id,
            )

        return notify_response
    except WhatsAppProviderError as exc:
        store.log_event(
            app_id=app_id,
            event_type="erp_notify_template",
            payload=payload,
            status="error",
            phone=request_data.telefono,
            error_message=str(exc),
        )
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/notifications/recent")
def notifications_recent(
    limit: int = Query(default=50, ge=1, le=200),
    app_id: str = Depends(resolve_app_id),
) -> dict[str, Any]:
    return {"app_id": app_id, "items": store.list_recent(limit=limit, app_id=app_id)}
