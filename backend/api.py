import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- FIX: Pathing logic to find modules in the root ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import routers
from routes import (
    auth_router,
    analysis_router,
    groups_router,
    incidents_router,
    analytics_router,
    alerts_router,
    chat_router
)

from contextlib import asynccontextmanager
from workers.alert_worker import alert_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the alert worker
    await alert_worker.start()
    yield
    # Shutdown: Stop the alert worker
    await alert_worker.stop()

app = FastAPI(
    title="Cloud RCA - Self-Healing Dashboard",
    description="Backend API for Cloud Root Cause Analysis and Self-Healing System",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root Endpoint ---
@app.get("/")
async def root():
    return {
        "status": "Online",
        "service": "Cloud RCA Agent",
        "version": "1.0.0"
    }

# --- Include Routers ---
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(groups_router)
app.include_router(incidents_router)
app.include_router(analytics_router)
app.include_router(alerts_router)
app.include_router(chat_router)

# Legacy endpoint for backwards compatibility
from pydantic import BaseModel
from typing import Optional

class AnalyzeRequest(BaseModel):
    time_range_minutes: int = 60
    max_traces: Optional[int] = 10

@app.post("/api/analyze")
async def legacy_analyze_endpoint(request: AnalyzeRequest):
    """Legacy endpoint - redirects to /analyze/start"""
    try:
        from core.agent import run_analysis_for_api
        result = await run_analysis_for_api(
            time_range_minutes=request.time_range_minutes,
            max_traces=request.max_traces
        )
        return result
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)