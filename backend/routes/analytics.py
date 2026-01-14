import sys
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException
from google.cloud.firestore_v1.base_query import FieldFilter

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.agent import db
except ImportError:
    db = None

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Firebase is not initialized.")
    return db

@router.get("/summary")
async def get_analytics_summary():
    """Get summary analytics from real data"""
    conn = get_db()
    try:
        # Total anomalies in 24h
        now = datetime.now()
        day_ago = (now - timedelta(hours=24)).isoformat()
        daily_query = conn.collection("incidents").where(filter=FieldFilter("timestamp", ">=", day_ago)).count()
        daily_result = await daily_query.get()
        daily_count = daily_result[0][0].value

        # Critical issues (P0 or P1)
        critical_query = conn.collection("incidents").where(filter=FieldFilter("status", "==", "OPEN")).where(filter=FieldFilter("priority", "in", ["P0", "P1", "P0 (Auto-Escalated)"])).count()
        critical_result = await critical_query.get()
        critical_count = critical_result[0][0].value

        # Active incidents (All OPEN)
        active_query = conn.collection("incidents").where(filter=FieldFilter("status", "==", "OPEN")).count()
        active_result = await active_query.get()
        active_count = active_result[0][0].value

        # Avg Confidence and unique services from latest 50
        recent_docs = await conn.collection("incidents").order_by("timestamp", direction="DESCENDING").limit(50).get()
        confidences = []
        services = set()
        for d in recent_docs:
            data = d.to_dict()
            conf = data.get("analysis", {}).get("confidence", 0)
            if conf > 0: confidences.append(conf)
            if data.get("service_name"): services.add(data.get("service_name"))
        
        avg_confidence = round(sum(confidences) / len(confidences)) if confidences else 0
        
        # Health Score Logic: 100 - (active_count * 2) - (critical_count * 10)
        health_score = max(0, 100 - (active_count * 2) - (critical_count * 10))
        
        return {
            "totalErrors": daily_count,
            "activeGroups": active_count,
            "criticalIssues": critical_count,
            "healthScore": health_score,
            "avgConfidence": avg_confidence,
            "impactedServices": len(services)
        }
    except Exception as e:
        print(f"Analytics Error: {e}")
        return {
            "totalErrors": 0,
            "activeGroups": 0,
            "criticalIssues": 0,
            "healthScore": 100,
            "avgConfidence": 0,
            "impactedServices": 0
        }

@router.get("/trends")
async def get_analytics_trends(range: str = "7d"):
    """Get trend data aggregated from Firestore"""
    conn = get_db()
    try:
        # Determine time threshold
        now = datetime.now()
        if range == "24h":
            delta = timedelta(hours=24)
            group_by = "hour"
        elif range == "30d":
            delta = timedelta(days=30)
            group_by = "day"
        else: # 7d default
            delta = timedelta(days=7)
            group_by = "day"
            
        threshold = (now - delta).isoformat()
        
        # Query incidents within range
        docs = await conn.collection("incidents").where(filter=FieldFilter("timestamp", ">=", threshold)).get()
        
        trends = {}
        categories = {}
        status_dist = {"OPEN": 0, "RESOLVED": 0, "INVESTIGATING": 0}
        risk_matrix = []
        
        for doc in docs:
            data = doc.to_dict()
            ts_str = data.get("timestamp")
            if not ts_str: continue
            
            ts = datetime.fromisoformat(ts_str)
            
            # Trend grouping
            if group_by == "hour":
                key = ts.strftime("%H:00")
            else:
                key = ts.strftime("%b %d")
                
            if key not in trends:
                trends[key] = {"date": key, "errors": 0, "anomalies": 0}
            trends[key]["errors"] += data.get("occurrence_count", 1)
            trends[key]["anomalies"] += 1
            
            # Category grouping
            svc = data.get("service_name", "Unknown")
            categories[svc] = categories.get(svc, 0) + data.get("occurrence_count", 1)
            
            # Status distribution
            status = data.get("status", "OPEN")
            status_dist[status] = status_dist.get(status, 0) + 1

            # Scatter data (Risk Matrix)
            analysis = data.get("analysis", {})
            confidence = analysis.get("confidence", 0)
            if isinstance(confidence, (int, float)) and confidence <= 1.0:
                confidence = round(confidence * 100)
                
            risk_matrix.append({
                "confidence": confidence,
                "impact": data.get("occurrence_count", 1),
                "service": svc,
                "label": analysis.get("cause", "Unknown"),
                "id": doc.id[:8]
            })

        # Format trends for frontend (sorted by time)
        sorted_trends = sorted(trends.values(), key=lambda x: x['date'])
        
        # Format categories
        top_categories = [{"name": k, "value": v} for k, v in categories.items()]
        top_categories = sorted(top_categories, key=lambda x: x['value'], reverse=True)[:5]
        
        # Format status
        status_distribution = [{"name": k.capitalize(), "value": v} for k, v in status_dist.items()]
        
        return {
            "trends": sorted_trends,
            "topCategories": top_categories,
            "statusDistribution": status_distribution,
            "riskMatrix": risk_matrix[:30] # Limit for UI clarity
        }
    except Exception as e:
        print(f"Trends Error: {e}")
        return {"trends": [], "topCategories": [], "statusDistribution": []}
