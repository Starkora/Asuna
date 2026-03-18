import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    app_port: int
    app_debug: bool
    erp_api_key: str
    whatsapp_token: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    whatsapp_app_secret: str
    whatsapp_api_version: str
    request_timeout_seconds: int
    sqlite_path: str



def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Asuna WhatsApp Bot"),
        app_env=os.getenv("APP_ENV", "development"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        app_debug=_env_bool("APP_DEBUG", True),
        erp_api_key=os.getenv("ERP_API_KEY", ""),
        whatsapp_token=os.getenv("WHATSAPP_TOKEN", ""),
        whatsapp_phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        whatsapp_verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", ""),
        whatsapp_app_secret=os.getenv("WHATSAPP_APP_SECRET", ""),
        whatsapp_api_version=os.getenv("WHATSAPP_API_VERSION", "v20.0"),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        sqlite_path=os.getenv("SQLITE_PATH", "./notifications.db"),
    )
