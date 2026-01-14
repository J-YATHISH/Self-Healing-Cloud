from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.agent import db
except ImportError:
    db = None

router = APIRouter(prefix="/alerts", tags=["Alerts"])

class AlertRule(BaseModel):
    name: str
    category: str
    threshold: int
    window_minutes: int
    severity: str
    enabled: bool = True

def get_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Firebase is not initialized.")
    return db

@router.get("/rules")
async def list_alert_rules():
    """List all alert rules"""
    conn = get_db()
    try:
        docs = await conn.collection("alert_rules").get()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    except:
        return []

@router.post("/rules")
async def create_alert_rule(rule: AlertRule):
    """Create a new alert rule"""
    conn = get_db()
    try:
        # Use model_dump() in Pydantic v2 or dict() in v1
        rule_data = rule.dict()
        doc_ref = await conn.collection("alert_rules").add(rule_data)
        return {"status": "created", "id": doc_ref[1].id}
    except Exception as e:
        print(f"❌ Error creating alert rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rules/{rule_id}")
async def update_alert_rule(rule_id: str, rule: AlertRule):
    """Update an existing alert rule"""
    conn = get_db()
    try:
        await conn.collection("alert_rules").document(rule_id).update(rule.dict())
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{rule_id}")
async def delete_alert_rule(rule_id: str):
    """Delete an alert rule"""
    conn = get_db()
    try:
        await conn.collection("alert_rules").document(rule_id).delete()
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
