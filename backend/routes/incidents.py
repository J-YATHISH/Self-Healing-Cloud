from fastapi import APIRouter, HTTPException
from typing import Optional
from google.cloud.firestore_v1.base_query import FieldFilter
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.agent import db
except ImportError:
    db = None

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def get_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Firebase is not initialized.")
    return db

@router.get("")
async def list_incidents(group_id: Optional[str] = None, page: int = 1, limit: int = 10):
    """List all incidents, optionally filtered by group, with pagination and sorting"""
    conn = get_db()
    try:
        from google.cloud.firestore import Query
        query = conn.collection("incidents").order_by("timestamp", direction=Query.DESCENDING)
        
        if group_id:
            query = query.where(filter=FieldFilter("trace_id", "==", group_id))
            
        # Simple pagination using offset (reasonable for small/medium datasets)
        offset = (page - 1) * limit
        docs = await query.offset(offset).limit(limit).get()
        
        res = []
        for doc in docs:
            data = doc.to_dict()
            res.append({
                "id": doc.id,
                "trace_id": data.get("trace_id"),
                "service_name": data.get("service_name"),
                "created_at": data.get("timestamp"),
                "priority": data.get("priority"),
                "status": "OPEN"
            })
        return res
    except Exception as e:
        return []

@router.get("/{id}")
async def get_incident_detail(id: str):
    """Get detailed information about a specific incident"""
    conn = get_db()
    try:
        doc = await conn.collection("incidents").document(id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        data = doc.to_dict()
        return {
            "id": doc.id,
            "trace_id": data.get("trace_id"),
            "service_name": data.get("service_name"),
            "timestamp": data.get("timestamp"),
            "analysis": data.get("analysis", {}),
            "logs": data.get("logs", []),
            "priority": data.get("priority"),
            "status": "OPEN"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
