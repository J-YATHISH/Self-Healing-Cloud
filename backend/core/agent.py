import os
import sys
import json
import asyncio
# import httpx - Moved inside function
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from collections import Counter

# --- FIX: Ensure Python can find modules in the parent directory ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- 1. LIVE INTEGRATION ---
try:
    from services.log_collector import authenticate, fetch_logs
    print("📡 Live Log Collector module loaded successfully.")
except ImportError as e:
    print(f"❌ CRITICAL ERROR: log_collector.py not found ({e}). Live fetching is impossible.")
    raise

# --- 2. CONFIGURATION ---
# Load .env from backend root (parent of core/)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(parent_dir, ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

# --- 3. FIREBASE INITIALIZATION ---
def init_firebase():
    """Initializes Firebase and returns a Firestore client.
    Forces REST transport via environment variable to avoid gRPC connection hangs.
    """
    try:
        # Force REST transport globally for this process
        os.environ["GOOGLE_CLOUD_FIRESTORE_FORCE_REST"] = "true"
        
        if not firebase_admin._apps:
            # Look for serviceAccountKey.json in the backend/ root (parent of core/)
            key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "serviceAccountKey.json")
            if os.path.exists(key_path):
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
                print(f"✅ Firebase initialized successfully (Forced REST from {key_path}).")
            else:
                print(f"⚠️ serviceAccountKey.json missing at {key_path}.")
                return None
        
        # Standard client now honors the environment variable
        return firestore.AsyncClient()
    except Exception as e:
        print(f"❌ Firebase Init Error: {e}")
        return None

db = init_firebase()

# --- 4. THE AI BRAIN (ASYNC) ---
async def analyze_logs_async(log_data):
    print("🛡️ AI Brain: Performing Deep Analysis on Cloud Traces...")
    prompt = (
        "You are an expert Google Cloud SRE and Security Agent. Analyze these logs: "
        f"{json.dumps(log_data)} "
        "\nReturn ONLY a JSON object with: cause, category, confidence, action, security_alert, redacted_summary, priority, correlation_insight."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1}
    }
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json=payload, timeout=30.0)
            if response.status_code == 200:
                res_json = response.json()
                return json.loads(res_json['candidates'][0]['content']['parts'][0]['text'])
        return None
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

# --- 5. PROCESS TRACE (ASYNC) ---
async def process_trace_async(trace_id, logs):
    print(f"🧵 ANALYZING TRACE: {trace_id}")
    analysis = await analyze_logs_async({"logs": logs})
    if analysis:
        if len(logs) > 5: analysis['priority'] = "P0 (Auto-Escalated)"
        if db:
            try:
                # Store first 20 logs as context for the Investigation Canvas
                log_context = logs[:20]
                service_name = logs[0].get('service', 'unknown') if logs else 'unknown'
                
                # Normalize confidence to 0-100 range
                confidence = analysis.get('confidence', 0)
                if isinstance(confidence, (int, float)) and confidence <= 1.0:
                    confidence = round(confidence * 100)
                analysis['confidence'] = confidence

                await db.collection("incidents").add({
                    "trace_id": trace_id,
                    "service_name": service_name,
                    "timestamp": datetime.now().isoformat(),
                    "occurrence_count": len(logs),
                    "security_alert": analysis.get('security_alert', False),
                    "redacted_text": analysis.get('redacted_summary'),
                    "priority": analysis.get('priority', 'P2'),
                    "correlation": analysis.get('correlation_insight', 'N/A'),
                    "analysis": analysis,
                    "logs": log_context,
                    "status": "OPEN" # Explicitly set for aggregation
                })
            except Exception as e: print(f"❌ Firebase Error: {e}")
        return (trace_id, logs, analysis)
    return (trace_id, logs, None)

# --- 6. LIVE WRAPPER (ASYNC) ---
async def run_analysis_for_api(time_range_minutes=60, max_traces=10, user_id="default_user"):
    """
    Run analysis using stored user credentials (FAST ASYNC VERSION)
    """
    try:
        from services.credential_manager import get_credentials
        if db is None:
            return {"results": [], "error": "Firebase not initialized"}
        
        try:
            creds = await get_credentials(db, user_id)
            cred_doc = await db.collection('user_credentials').document(user_id).get()
            project_id = cred_doc.to_dict().get('project_id') if cred_doc.exists else None
            
            if not project_id:
                print(f"⚠️ WARNING: No project_id found for user {user_id}. Using default.")
            
            if not creds or not creds.token:
                raise ValueError("Credentials retrieved but token is missing or empty")
                
            print(f"📋 Using project_id: {project_id} for user: {user_id}")
            print(f"🔑 Token starts with: {creds.token[:10]}... (Len: {len(creds.token)})")
        except ValueError as e:
            print(f"❌ Auth Error for user {user_id}: {str(e)}")
            return {"results": [], "error": f"No valid credentials: {str(e)}"}
        
        # 1. Fetch Logs (Sync call group)
        traces = fetch_logs(creds, time_range_minutes=time_range_minutes, project_id=project_id)
        if not traces: 
            return {"results": []}
        
        # 2. Parallel AI Analysis
        tasks = []
        selected_traces = list(traces.items())[:max_traces]
        for trace_id, log_list in selected_traces:
            tasks.append(process_trace_async(trace_id, log_list))
        
        completed_analyses = await asyncio.gather(*tasks)
            
        # 3. Format Results
        results = []
        for trace_id, log_list, analysis in completed_analyses:
            if analysis:
                results.append({
                    "trace_id": trace_id,
                    "category": analysis.get("category"),
                    "priority": analysis.get("priority"),
                    "log_count": len(log_list),
                    "root_cause": analysis.get("cause"),
                    "redacted_text": analysis.get("redacted_summary"),
                    "action": analysis.get("action"),
                    "correlation": analysis.get("correlation_insight"),
                    "security_alert": analysis.get("security_alert"),
                    "confidence": analysis.get("confidence")
                })
        
        print(f"🚀 Parallel Analysis Complete. Generated {len(results)} insights.")
        return {"results": results}
    except Exception as e:
        print(f"❌ run_analysis_for_api Error: {e}")
        return {"results": [], "error": str(e)}

# --- 7. CHATBOT LOGIC (ASYNC) ---
async def chat_with_ai_async(message, user_id="default_user"):
    """
    Chat with Gemini using broad incident context.
    """
    print(f"💬 Chat request from {user_id}: {message[:50]}...")
    
    context_data = []
    if db:
        try:
            # Fetch last 50 incidents for broad context
            docs = await db.collection("incidents").order_by("timestamp", direction="DESCENDING").limit(50).get()
            for doc in docs:
                d = doc.to_dict()
                context_data.append({
                    "id": d.get("trace_id", doc.id)[:8],
                    "service": d.get("service_name"),
                    "cause": d.get("analysis", {}).get("cause"),
                    "confidence": d.get("analysis", {}).get("confidence"),
                    "priority": d.get("priority"),
                    "time": d.get("timestamp")
                })
        except Exception as e:
            print(f"⚠️ Failed to fetch chat context: {e}")

    prompt = (
        "You are 'Reliability Chatbot', a high-performance SRE assistant. "
        "Your goal is to help users understand system health and incidents. "
        "Return a concise, expert reply. Do NOT mention you can take autonomous actions. "
        "If the user asks for suggestions, provide concrete remediation steps. "
        f"\n\nIncident Context (Latest 50):\n{json.dumps(context_data)}"
        f"\n\nUser Message: {message}"
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2} # Low temp for factual SRE advice
    }
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json=payload, timeout=20.0)
            if response.status_code == 200:
                res_json = response.json()
                return {"reply": res_json['candidates'][0]['content']['parts'][0]['text']}
        return {"reply": "I'm having trouble connecting to my brain. Please try again."}
    except Exception as e:
        print(f"❌ Chat Gemini Error: {e}")
        return {"reply": "An error occurred while processing your request."}

if __name__ == "__main__":
    run_analysis_for_api(time_range_minutes=120, max_traces=5)