from typing import Any

from fastapi import APIRouter

from core.container import settings, store

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": settings.app_name,
        "env": settings.app_env,
    }


@router.get("/health/live")
def health_live() -> dict[str, Any]:
    return {"ok": True}


@router.get("/health/ready")
def health_ready() -> dict[str, Any]:
    checks = {
        "db": store.is_healthy(),
        "erp_api_key": bool(settings.erp_api_key or settings.erp_api_keys),
        "whatsapp_verify_token": bool(settings.whatsapp_verify_token),
        "whatsapp_token": bool(settings.whatsapp_token),
        "whatsapp_phone_number_id": bool(settings.whatsapp_phone_number_id),
    }
    ready = all(checks.values())
    return {
        "ok": ready,
        "checks": checks,
        "default_app_id": settings.default_app_id,
        "configured_apps": sorted(list(settings.erp_api_keys.keys())),
    }
