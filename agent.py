import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from collections import Counter

# Import existing collector functions
from log_collector import authenticate, fetch_logs, load_logs_from_json, list_saved_logs

# --- 1. LOAD CONFIG ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# REST URL for Gemini 3 Flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

# --- 2. INITIALIZE FIREBASE SAFELY ---
def init_firebase():
    """Initializes Firebase safely by checking for existing instances."""
    try:
        app = firebase_admin.get_app()
        print("✅ Using existing Firebase app.")
    except ValueError:
        key_path = "serviceAccountKey.json"
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully.")
        else:
            print("❌ serviceAccountKey.json not found! Cannot initialize.")
            return None
    return firestore.client()

db = init_firebase()

# --- 3. PATTERN ENGINE ---
def get_historical_patterns(logs):
    """Calculates frequency of similar error messages in the batch."""
    messages = [log.get('message', '') for log in logs]
    return Counter(messages)

# --- 4. THE BRAIN: CALL GEMINI ---
# --- UPDATED BRAIN: ADDING CORRELATION & PRIORITY ---
def analyze_logs(log_data):
    """Uses Gemini 3 for RCA, PII redaction, and Error Correlation."""
    print("🧠 AI Brain: Performing RCA and Correlation Analysis...")
    
    # We update the prompt to handle Feature 2 (Priority) and Feature 3 (Correlation)
    prompt = (
        "You are an expert SRE. Analyze these logs: "
        f"{json.dumps(log_data)} "
        "\nPerform the following: "
        "1. RCA: What is the root cause? "
        "2. Security: Redact PII in 'redacted_summary'. "
        "3. Correlation: If there are multiple different errors, explain if they are related (e.g., OOM causing Timeouts). "
        "4. Priority: Assign P0 (Critical), P1 (High), or P2 (Medium) based on frequency and severity. "
        "Return ONLY a JSON object with: 'cause', 'category', 'confidence', 'action', "
        "'security_alert', 'redacted_summary', 'priority', 'correlation_insight'."
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1}
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])
        return None
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# --- UPDATED PROCESS TRACE ---
def process_trace(trace_id, logs):
    print(f"\n🧵 PROCESSING TRACE: {trace_id}")
    
    # Feature 2: Historical Pattern Check (Frequency)
    total_logs = len(logs)
    
    analysis = analyze_logs({"logs": logs})
    
    if analysis:
        # Override priority if frequency is too high
        if total_logs > 5:
            analysis['priority'] = "P0 (Auto-Escalated due to high frequency)"
        
        # Display the new features in console
        print(f"📡 PRIORITY: {analysis.get('priority')}")
        print(f"🔗 CORRELATION: {analysis.get('correlation_insight')}")
        print(f"🛡️ REDACTED: {analysis.get('redacted_summary')}")

        if db:
            db.collection("incidents").add({
                "trace_id": trace_id,
                "timestamp": datetime.now().isoformat(),
                "occurrence_count": total_logs,
                "priority": analysis.get('priority'),
                "correlation": analysis.get('correlation_insight'),
                "security_alert": analysis.get('security_alert'),
                "redacted_text": analysis.get('redacted_summary'),
                "analysis": analysis
            })
            print("✅ Firebase updated with Escalation and Correlation.")

# --- 7. ORCHESTRATOR ---
def run_prototype(mode="load", log_filename="mock_logs.json"):
    """Runs the analysis pipeline using local mock data."""
    if not os.path.exists("data"): os.makedirs("data")
    
    filepath = os.path.join("data", log_filename)
    if not os.path.exists(filepath):
        print(f"❌ Error: {filepath} not found.")
        return

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Convert list to mock trace format for the loop
    mock_traces = {"MOCK_TRACE_123": data}
    
    for trace_id, logs in mock_traces.items():
        process_trace(trace_id, logs)
# --- ADD THIS TO THE BOTTOM OF agent.py ---

def run_analysis_for_api(time_range_minutes=60, max_traces=10):
    """
    Wrapper function for api.py to call.
    It runs the analysis and returns a structured list for the UI.
    """
    print(f"🚀 API-Triggered Analysis: {time_range_minutes}m range")
    
    # In 'load' mode for your local testing with mock_logs.json
    # If you want to fetch live GCP logs, change mode to "fetch"
    if not os.path.exists("data/mock_logs.json"):
        return {"results": [], "message": "Mock file not found"}

    with open("data/mock_logs.json", "r") as f:
        logs = json.load(f)

    # We treat the mock data as one trace for the dashboard
    trace_id = "MOCK_TRACE_" + datetime.now().strftime("%H%M%S")
    
    # Call the core processing logic
    analysis = process_trace(trace_id, logs)
    
    if analysis:
        # Format the result specifically for what the api.py HTML expects
        return {
            "results": [{
                "trace_id": trace_id,
                "category": analysis.get("category", "Uncategorized"),
                "priority": analysis.get("priority", "P2"),
                "log_count": len(logs),
                "root_cause": analysis.get("cause", "Unknown"),
                "redacted_text": analysis.get("redacted_summary", ""),
                "action": analysis.get("action", "No action"),
                "correlation": analysis.get("correlation_insight", "N/A"),
                "security_alert": analysis.get("security_alert", False),
                "confidence": analysis.get("confidence", 0)
            }]
        }
    
    return {"results": [], "message": "Analysis produced no results"}
if __name__ == "__main__":
    run_prototype()