from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
import app.models  # Ensure all models are registered
from app.routers import (
    fixed_schedule_router,
    tasks_router,
    reviews_router,
    plans_router,
    dashboard_router,
)

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI Local-First Daily Life Operating System",
    version="1.0.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(fixed_schedule_router)
app.include_router(tasks_router)
app.include_router(reviews_router)
app.include_router(plans_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "LifeOS Agentic Planner API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
