from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.legal import router as legal_router
from api.routes.notifications import router as notifications_router
from api.routes.webhook import router as webhook_router
from core.container import settings, store


app = FastAPI(title=settings.app_name, version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    store.init_db()


app.include_router(health_router)
app.include_router(legal_router)
app.include_router(webhook_router)
app.include_router(notifications_router)
