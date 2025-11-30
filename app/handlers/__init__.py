from .announcements import router as announcements
from .orders import router as orders
from .documents import router as documents
from .events import router as events
from .contacts import router as contacts
from .admin_panel import router as admin_panel
from .auth import router as auth
from .start import router as start

__all__ = [
    "announcements",
    "orders",
    "documents",
    "events",
    "contacts",
    "admin_panel",
    "auth",
    "start"
]
