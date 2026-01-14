# Routes package initialization
from fastapi import APIRouter

# Import all routers
from .auth import router as auth_router
from .analysis import router as analysis_router
from .groups import router as groups_router
from .incidents import router as incidents_router
from .analytics import router as analytics_router
from .alerts import router as alerts_router
from .chat import router as chat_router

# Export all routers
__all__ = [
    "auth_router",
    "analysis_router",
    "groups_router",
    "incidents_router",
    "analytics_router",
    "alerts_router",
    "chat_router"
]
