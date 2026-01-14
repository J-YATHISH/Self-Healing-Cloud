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
async def list_groups(status: Optional[str] = None, page: int = 1, limit: int = 10):
    """
    Lists incident groups. 
    Currently maps 1:1 to incidents since we don't have grouping logic in DB yet.
    """
    conn = get_db()
    try:
        # Import Query for ordering
        from google.cloud.firestore import Query
        
        # Start with base query, order by timestamp descending
        query = conn.collection("incidents").order_by("timestamp", direction=Query.DESCENDING)
        
        # Increase limit since we aggregate by trace_id (multiple incidents might share a trace)
        # Limit the scope of aggregation to the last 100 incidents for performance
        docs = await query.limit(100).get() 
        
        groups_map = {}
        for doc in docs:
            data = doc.to_dict()
            trace_id = data.get("trace_id", doc.id)
            analysis = data.get("analysis", {})
            
            if trace_id not in groups_map:
                groups_map[trace_id] = {
                    "id": trace_id,
                    "name": analysis.get("cause", "Unknown Anomaly"),
                    "status": "OPEN",
                    "severity": data.get("priority", "P2"),
                    "count": data.get("occurrence_count", 1),
                    "last_seen": data.get("timestamp"),
                    "root_cause": {
                        "cause": analysis.get("cause"),
                        "confidence": round(analysis.get("confidence", 0) * 100) if analysis.get("confidence", 0) <= 1.0 else analysis.get("confidence", 0)
                    },
                    "services": [data.get("service_name", "Unknown")],
                    "route": "GCP Cloud Run"
                }
            else:
                groups_map[trace_id]["count"] += data.get("occurrence_count", 1)
                if data.get("timestamp") and (not groups_map[trace_id]["last_seen"] or data.get("timestamp") > groups_map[trace_id]["last_seen"]):
                    groups_map[trace_id]["last_seen"] = data.get("timestamp")
            
        # Sort aggregated groups by last_seen descending
        sorted_groups = sorted(groups_map.values(), key=lambda x: x['last_seen'] or '', reverse=True)
        
        # Pagination: pages of 10
        start = (page - 1) * limit
        end = start + limit
        return sorted_groups[start:end]
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
