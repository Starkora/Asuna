import hashlib
import hmac

from fastapi import HTTPException, status


def _normalize_app_id(app_id: str | None, default_app_id: str) -> str:
    normalized = (app_id or default_app_id or "default").strip().lower()
    return normalized or "default"


def validate_api_key(
    received_api_key: str | None,
    expected_api_key: str,
    app_id: str | None,
    app_api_keys: dict[str, str],
    default_app_id: str,
) -> str:
    resolved_app_id = _normalize_app_id(app_id, default_app_id)

    if app_api_keys:
        expected_for_app = app_api_keys.get(resolved_app_id)
        if not expected_for_app:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"app_id no permitido: {resolved_app_id}",
            )

        if not received_api_key or not hmac.compare_digest(received_api_key, expected_for_app):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key invalida",
            )
        return resolved_app_id

    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ERP_API_KEY no configurado en el servidor",
        )

    if not received_api_key or not hmac.compare_digest(received_api_key, expected_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key invalida",
        )

    return resolved_app_id


def verify_meta_signature(raw_body: bytes, signature_header: str | None, app_secret: str) -> bool:
    if not app_secret:
        return True

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    received_signature = signature_header.replace("sha256=", "", 1)
    expected_signature = hmac.new(
        app_secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(received_signature, expected_signature)
