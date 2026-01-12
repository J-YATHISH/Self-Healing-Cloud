import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from collections import Counter

# Import existing collector functions from your local file
try:
    from log_collector import authenticate, fetch_logs, load_logs_from_json, list_saved_logs
except ImportError:
    print("⚠️ log_collector.py not found. Live fetching will be disabled.")

# --- 1. CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Using the specific REST endpoint for Gemini 3 Flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

# --- 2. FIREBASE INITIALIZATION ---
def init_firebase():
    """Initializes Firebase safely by checking for existing instances."""
    try:
        app = firebase_admin.get_app()
        return firestore.client()
    except ValueError:
        key_path = "serviceAccountKey.json"
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully.")
            return firestore.client()
        else:
            print("❌ serviceAccountKey.json not found! Firebase functions disabled.")
            return None

db = init_firebase()

# --- 3. PATTERN ENGINE ---
def get_historical_patterns(logs):
    """Calculates frequency of similar error messages in the batch."""
    messages = [log.get('message', log.get('textPayload', '')) for log in logs]
    return Counter(messages)

# --- 4. THE AI BRAIN (RCA, SECURITY, CORRELATION) ---
def analyze_logs(log_data):
    """Calls Gemini 3 to perform RCA, PII redaction, and error correlation."""
    print("🛡️ AI Brain: Performing RCA and Security Scan...")
    
    prompt = (
        "You are an expert Google Cloud SRE and Security Agent. Analyze these logs: "
        f"{json.dumps(log_data)} "
        "\nPerform the following and return ONLY a JSON object: "
        "1. cause: What is the technical root cause? "
        "2. category: (e.g., Auth, Database, Network, Memory). "
        "3. confidence: A float between 0 and 1. "
        "4. action: Short, actionable remediation step. "
        "5. security_alert: Boolean. True if PII (passwords, keys, secrets) are found. "
        "6. redacted_summary: A summary where all PII/secrets are replaced by [REDACTED]. "
        "7. priority: P0, P1, or P2 based on severity. "
        "8. correlation_insight: If multiple logs exist, explain how they relate (e.g., OOM leading to Timeout)."
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_text)
        else:
            print(f"❌ Gemini API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

# --- 5. PROCESS TRACE ---
def process_trace(trace_id, logs):
    """Core logic to process logs, analyze them, and sync to Firebase."""
    print(f"\n{'='*60}\n🧵 PROCESSING TRACE: {trace_id}\n{'='*60}")
    
    # 1. Frequency Patterns
    patterns = get_historical_patterns(logs)
    total_logs = len(logs)
    
    # 2. AI Analysis
    analysis = analyze_logs({"logs": logs})
    
    if analysis:
        # Type Safety: Ensure confidence is a float
        try:
            conf_score = float(analysis.get('confidence', 0))
        except:
            conf_score = 0.0
            
        # Feature: Auto-Escalation Logic
        if total_logs > 5:
            analysis['priority'] = "P0 (Auto-Escalated)"

        # --- CONSOLE OUTPUT FOR TESTING ---
        print(f"\n📡 PRIORITY: {analysis.get('priority')}")
        print(f"🔗 CORRELATION: {analysis.get('correlation_insight')}")
        if analysis.get('security_alert'):
            print("🚨 SECURITY ALERT: PII Detected and Redacted!")
        print(f"🔍 RCA: {analysis.get('cause')}")
        print(f"🛡️ REDACTED: {analysis.get('redacted_summary')}")

        # 3. FIREBASE SYNC
        if db:
            try:
                incident_data = {
                    "trace_id": trace_id,
                    "timestamp": datetime.now().isoformat(),
                    "occurrence_count": total_logs,
                    "security_alert": analysis.get('security_alert', False),
                    "redacted_text": analysis.get('redacted_summary'),
                    "priority": analysis.get('priority', 'P2'),
                    "correlation": analysis.get('correlation_insight', 'N/A'),
                    "analysis": {
                        "cause": analysis.get('cause'),
                        "category": analysis.get('category'),
                        "action": analysis.get('action'),
                        "confidence": conf_score
                    },
                    "status": "AUTO-RESOLVED" if conf_score > 0.8 else "PENDING_REVIEW"
                }
                db.collection("incidents").add(incident_data)
                print("✅ Firebase updated.")
            except Exception as e:
                print(f"❌ Firebase error: {e}")
        
        return analysis
    return None

# --- 6. WRAPPER FOR API.PY ---
def run_analysis_for_api(time_range_minutes=60, max_traces=10):
    """Function called by the FastAPI frontend."""
    # Check for mock data first
    filepath = "data/mock_logs.json"
    if not os.path.exists(filepath):
        return {"results": [], "message": "No logs found"}

    with open(filepath, "r") as f:
        logs = json.load(f)

    trace_id = "MOCK_TRACE_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis = process_trace(trace_id, logs)
    
    if analysis:
        # Re-mapping keys for API consistency
        return {
            "results": [{
                "trace_id": trace_id,
                "category": analysis.get("category"),
                "priority": analysis.get("priority"),
                "log_count": len(logs),
                "root_cause": analysis.get("cause"),
                "redacted_text": analysis.get("redacted_summary"),
                "action": analysis.get("action"),
                "correlation": analysis.get("correlation_insight"),
                "security_alert": analysis.get("security_alert"),
                "confidence": analysis.get("confidence")
            }]
        }
    return {"results": []}

# --- 7. MAIN ORCHESTRATOR (LOCAL TESTING) ---
def run_prototype():
    """Runs the agent using the local mock_logs.json file."""
    if not os.path.exists("data"): os.makedirs("data")
    
    filepath = "data/mock_logs.json"
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        process_trace("MOCK_TRACE_LOCAL", data)
    else:
        print("❌ data/mock_logs.json not found.")

if __name__ == "__main__":
    run_prototype()