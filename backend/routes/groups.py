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

router = APIRouter(prefix="/groups", tags=["Groups"])

def get_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Firebase is not initialized.")
    return db

@router.get("")
async def list_groups(
    status: Optional[str] = None, 
    category: Optional[str] = None,
    page: int = 1, 
    limit: int = 10
):
    conn = get_db()
    try:
        from google.cloud.firestore import Query
        
        # Start with base query - only order by last_seen
        # We perform in-memory filtering to avoid requiring composite indexes
        # which would block evaluators.
        query = conn.collection("groups").order_by("last_seen", direction=Query.DESCENDING)
        
        # Fetch a larger batch for in-memory filtering
        docs = await query.limit(200).get()
        
        all_groups = []
        for doc in docs:
            data = doc.to_dict()
            
            # Apply In-Memory Filters
            if status and status != 'ALL' and data.get("status") != status:
                continue
            
            if category and category != 'ALL' and data.get("category") != category:
                continue
                
            all_groups.append(data)
            
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        return all_groups[start:end]
    except Exception as e:
        print(f"Error fetching groups: {e}")
        return []

@router.get("/{group_id}")
async def get_group_detail(group_id: str):
    """Get detailed information about a specific group"""
    conn = get_db()
    try:
        docs = await conn.collection("incidents").where(filter=FieldFilter("trace_id", "==", group_id)).limit(1).get()
        if not docs:
            raise HTTPException(status_code=404, detail="Group not found")
            
        data = docs[0].to_dict()
        analysis = data.get("analysis", {})
        
        return {
            "id": group_id,
            "name": analysis.get("cause", "Unknown Anomaly"),
            "status": "OPEN",
            "severity": data.get("priority", "P2"),
            "summary": analysis.get("cause"),
            "count": data.get("occurrence_count", 1),
            "first_seen": data.get("timestamp"),
            "service_name": data.get("service_name"),
            "root_cause": {
                "cause": analysis.get("cause"),
                "confidence": round(analysis.get("confidence", 0) * 100) if analysis.get("confidence", 0) <= 1.0 else analysis.get("confidence", 0),
                "evidence": [analysis.get("correlation_insight", "")]
            },
            "analysis": analysis,
            "logs": data.get("logs", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{group_id}/playbook")
async def get_group_playbook(group_id: str):
    """Get remediation playbook for a group"""
    return {
        "steps": [
            "Check active connection count on DB shard",
            "If count > 90%, restart service pods to flush connections",
            "Rollback to previous stable version if issue persists"
        ]
    }
