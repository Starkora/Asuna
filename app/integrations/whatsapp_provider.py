import time

import requests

from core.config import Settings


class WhatsAppProviderError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def _get_messages_url(settings: Settings) -> str:
    if not settings.whatsapp_token:
        raise WhatsAppProviderError("WHATSAPP_TOKEN no configurado")
    if not settings.whatsapp_phone_number_id:
        raise WhatsAppProviderError("WHATSAPP_PHONE_NUMBER_ID no configurado")

    return (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )


def _get_headers(settings: Settings) -> dict:
    return {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }


def _post_with_retry(settings: Settings, payload: dict) -> dict:
    url = _get_messages_url(settings)
    headers = _get_headers(settings)

    last_exception: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=settings.request_timeout_seconds,
            )
            try:
                body = response.json() if response.content else {}
            except ValueError:
                body = {"raw": response.text}

            if response.status_code >= 400:
                raise WhatsAppProviderError(
                    f"Meta API error {response.status_code}: {body}",
                    status_code=response.status_code,
                )

            return body
        except WhatsAppProviderError:
            raise
        except Exception as exc:
            last_exception = exc
            if attempt < 3:
                time.sleep(attempt)

    if isinstance(last_exception, WhatsAppProviderError):
        raise last_exception

    raise WhatsAppProviderError(str(last_exception))


def send_whatsapp_text(settings: Settings, telefono: str, mensaje: str) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": mensaje},
    }

    return _post_with_retry(settings, payload)


def send_whatsapp_template(
    settings: Settings,
    telefono: str,
    template_name: str,
    language_code: str,
    components: list[dict] | None = None,
) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }

    if components:
        payload["template"]["components"] = components

    return _post_with_retry(settings, payload)
