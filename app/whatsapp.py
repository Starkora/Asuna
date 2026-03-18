import time
import requests

from config import Settings


class WhatsAppProviderError(RuntimeError):
    pass


def send_whatsapp_text(settings: Settings, telefono: str, mensaje: str) -> dict:
    if not settings.whatsapp_token:
        raise WhatsAppProviderError("WHATSAPP_TOKEN no configurado")
    if not settings.whatsapp_phone_number_id:
        raise WhatsAppProviderError("WHATSAPP_PHONE_NUMBER_ID no configurado")

    url = (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": mensaje},
    }

    last_exception: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=settings.request_timeout_seconds,
            )
            body = response.json() if response.content else {}

            if response.status_code >= 400:
                raise WhatsAppProviderError(
                    f"Meta API error {response.status_code}: {body}"
                )

            return body
        except Exception as exc:
            last_exception = exc
            if attempt < 3:
                time.sleep(attempt)

    raise WhatsAppProviderError(str(last_exception))
