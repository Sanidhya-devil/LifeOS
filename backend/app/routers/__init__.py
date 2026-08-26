from app.routers.fixed_schedule import router as fixed_schedule_router
from app.routers.tasks import router as tasks_router
from app.routers.reviews import router as reviews_router
from app.routers.plans import router as plans_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "fixed_schedule_router",
    "tasks_router",
    "reviews_router",
    "plans_router",
    "dashboard_router",
]
