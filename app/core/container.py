from core.config import get_settings
from repositories.notification_store import NotificationStore

settings = get_settings()
store = NotificationStore(settings.sqlite_path)
