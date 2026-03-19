from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse

from core.container import settings, store
from core.security import verify_meta_signature

router = APIRouter(tags=["webhook"])


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query("", alias="hub.mode"),
    hub_verify_token: str = Query("", alias="hub.verify_token"),
    hub_challenge: str = Query("", alias="hub.challenge"),
) -> PlainTextResponse:
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return PlainTextResponse(content=hub_challenge, status_code=200)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Webhook verification failed",
    )


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> dict[str, Any]:
    raw_body = await request.body()

    if not verify_meta_signature(raw_body, x_hub_signature_256, settings.whatsapp_app_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    store.log_event(app_id="meta", event_type="incoming_webhook", payload=payload, status="received")

    return {"status": "received"}
