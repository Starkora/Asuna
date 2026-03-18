from pydantic import BaseModel, Field, field_validator


class NotifyRequest(BaseModel):
    telefono: str = Field(..., examples=["51987654321"])
    mensaje: str = Field(..., min_length=1, max_length=4096)

    @field_validator("telefono")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        normalized = value.replace(" ", "").replace("+", "")
        if not normalized.isdigit():
            raise ValueError("telefono debe contener solo digitos")
        if len(normalized) < 10 or len(normalized) > 15:
            raise ValueError("telefono debe tener entre 10 y 15 digitos")
        return normalized


class NotifyResponse(BaseModel):
    ok: bool
    message_id: str | None = None
    provider_response: dict | None = None
    deduplicated: bool = False
    idempotency_key: str | None = None
