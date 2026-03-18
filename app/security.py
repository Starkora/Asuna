import hashlib
import hmac
from fastapi import HTTPException, status


def validate_api_key(received_api_key: str | None, expected_api_key: str) -> None:
    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ERP_API_KEY no configurado en el servidor",
        )

    if not received_api_key or received_api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key invalida",
        )


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
