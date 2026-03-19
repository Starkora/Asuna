from fastapi import Header

from core.container import settings
from core.security import validate_api_key


def resolve_app_id(
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
    x_app_id: str | None = Header(default=None, alias="x-app-id"),
) -> str:
    return validate_api_key(
        received_api_key=x_api_key,
        expected_api_key=settings.erp_api_key,
        app_id=x_app_id,
        app_api_keys=settings.erp_api_keys,
        default_app_id=settings.default_app_id,
    )
