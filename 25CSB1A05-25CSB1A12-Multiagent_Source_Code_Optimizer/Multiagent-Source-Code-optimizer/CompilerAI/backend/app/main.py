from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes_health import router as health_router
from app.api.routes_runs import router as runs_router
from app.api.routes_events import router as events_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CompilerAI Run Service & Orchestrator API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(runs_router, prefix=settings.api_prefix)
app.include_router(events_router, prefix=settings.api_prefix)

@app.get("/")
def root():
    return {
        "message": "CompilerAI API is running",
        "health_check": f"{settings.api_prefix}/health",
        "documentation": "/docs"
    }
