from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import sys
import os
import base64
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.agent import run_analysis_for_api
except ImportError:
    run_analysis_for_api = None

router = APIRouter(prefix="/analyze", tags=["Analysis"])

class AnalyzeRequest(BaseModel):
    time_range_minutes: int = 60
    max_traces: Optional[int] = 10
    cluster_id: Optional[str] = None

@router.post("/start")
async def analyze_start(request: AnalyzeRequest, authorization: str = Header(None)):
    """Triggers the full Gemini-3 AI analysis pipeline."""
    print(f"📥 Received API Request: Lookback {request.time_range_minutes}m")
    
    # Extract user_id from authorization header
    user_id = "default_user"  # fallback
    if authorization and authorization.startswith('Bearer '):
        try:
            token = authorization.replace('Bearer ', '')
            user_data = json.loads(base64.b64decode(token))
            user_id = user_data.get('user_id', 'default_user')
            print(f"👤 Analysis requested by user: {user_id}")
        except Exception as e:
            print(f"⚠️ Failed to decode user token: {e}")
    
    try:
        if run_analysis_for_api is None:
            raise HTTPException(status_code=503, detail="Analysis service not available")
            
        result = await run_analysis_for_api(
            time_range_minutes=request.time_range_minutes,
            max_traces=request.max_traces,
            user_id=user_id  # Pass actual user_id
        )
        return result
    except Exception as e:
        print(f"❌ API Endpoint Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def analyze_status(task_id: str):
    """Get status of an analysis task"""
    return {"status": "completed", "progress": 100}
