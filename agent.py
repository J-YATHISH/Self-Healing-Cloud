import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Import log collector functions
from log_collector import authenticate, fetch_logs, load_logs_from_json, list_saved_logs


# --- 1. LOAD CONFIG ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# As per your list_models.py, we use this powerful Gemini 3 model
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"


# --- 2. INITIALIZE FIREBASE SAFELY ---
def init_firebase():
    """Initializes the default Firebase app if not already existing."""
    if not firebase_admin._apps:
        key_path = "serviceAccountKey.json"
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully.")
            return firestore.client()
        else:
            print("⚠️ serviceAccountKey.json not found! Firebase will be skipped.")
            return None
    return firestore.client()


db = init_firebase()


# --- 3. THE BRAIN: CALL GEMINI VIA REST ---
def analyze_logs(log_data):
    """Uses Gemini 3 to diagnose the root cause."""
    print("🤖 Analyzing logs with Gemini 3 Flash...")
    
    prompt = (
        "You are an SRE Agent. Analyze these Cloud Run error logs. "
        "Return ONLY a JSON object with keys: 'cause', 'category', 'confidence', 'action'. "
        f"Logs: {json.dumps(log_data)}"
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
        elif response.status_code == 429:
            print("⚠️ Rate limit hit. Please wait a moment.")
            return None
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None
_cached_credentials = None

def get_or_authenticate():
    """Get cached credentials or authenticate once"""
    global _cached_credentials
    
    if _cached_credentials is None:
        print("🔐 First time authentication required...")
        _cached_credentials = authenticate()
        print("✅ Credentials cached for this session")
    else:
        print("✅ Using cached credentials (no re-authentication needed)")
    
    return _cached_credentials

# --- 4. FETCH LOGS FROM GCP ---
def get_logs(mode="fetch", time_range_minutes=60, log_filename=None):
    """
    Get logs either by fetching from GCP or loading from saved file
    
    Args:
        mode: "fetch" (get new logs) or "load" (load saved logs)
        time_range_minutes: How many minutes back to fetch (for "fetch" mode)
        log_filename: Specific file to load (for "load" mode)
    
    Returns:
        Dictionary with log data
    """
    if mode == "fetch":
        print(f"📥 Fetching logs from GCP (last {time_range_minutes} minutes)...")
        creds = authenticate()
        traces = fetch_logs(creds, time_range_minutes=time_range_minutes, save_to_file=True)
        
        # Return in the format that includes metadata
        return {
            "fetch_time": datetime.utcnow().isoformat(),
            "total_traces": len(traces),
            "total_logs": sum(len(logs) for logs in traces.values()),
            "traces": traces
        }
    
    elif mode == "load":
        print(f"📂 Loading logs from saved file...")
        if log_filename is None:
            # List available files and use the most recent
            files = list_saved_logs()
            if not files:
                print("❌ No saved log files found. Use mode='fetch' to get new logs.")
                return None
            log_filename = sorted(files)[-1]  # Most recent file
            print(f"   Using most recent file: {log_filename}")
        
        return load_logs_from_json(log_filename)
    
    else:
        print(f"❌ Invalid mode: {mode}. Use 'fetch' or 'load'")
        return None


# --- 5. PROCESS EACH TRACE ---
def process_trace(trace_id, logs):
    """Analyze a single trace and store in Firebase"""
    print(f"\n{'='*80}")
    print(f"🧵 Processing Trace: {trace_id}")
    print(f"{'='*80}")
    
    # Prepare log summary for Gemini
    log_summary = {
        "trace_id": trace_id,
        "log_count": len(logs),
        "logs": []
    }
    
    for log in logs:
        log_summary["logs"].append({
            "timestamp": log["timestamp"],
            "severity": log["severity"],
            "service": log["service"],
            "message": log["message"],
            "root_cause": log.get("root_cause"),
            "suggestion": log.get("suggestion")
        })
    
    # Get AI Analysis
    analysis = analyze_logs(log_summary)
    
    if analysis:
        print(f"\n{'─'*40}")
        print(f"🔍 ROOT CAUSE: {analysis.get('cause', 'Unknown')}")
        print(f"📂 CATEGORY: {analysis.get('category', 'Unknown')}")
        print(f"💡 ACTION: {analysis.get('action', 'No action recommended')}")
        print(f"📊 CONFIDENCE: {analysis.get('confidence', 0)}")
        print(f"{'─'*40}")
        
        # Push to Firebase
        if db:
            try:
                doc_ref = db.collection("incidents").add({
                    "trace_id": trace_id,
                    "timestamp": datetime.now().isoformat(),
                    "service": logs[0]["service"] if logs else "unknown",
                    "log_count": len(logs),
                    "first_seen": logs[0]["timestamp"] if logs else None,
                    "last_seen": logs[-1]["timestamp"] if logs else None,
                    "analysis": analysis,
                    "status": "AUTO-RESOLVED" if analysis.get('confidence', 0) > 0.8 else "PENDING_REVIEW",
                    "raw_logs": log_summary["logs"]
                })
                print(f"✅ Firebase updated! (Doc ID: {doc_ref[1].id})")
            except Exception as e:
                print(f"❌ Failed to update Firebase: {e}")
        
        return analysis
    else:
        print("❌ Analysis failed. Check API Key or Quota.")
        return None


# --- 6. THE ORCHESTRATOR ---
def run_prototype(mode="fetch", time_range_minutes=60, log_filename=None, max_traces=None):
    """
    Main pipeline orchestrator
    
    Args:
        mode: "fetch" (get new logs from GCP) or "load" (use saved logs)
        time_range_minutes: For fetch mode - how many minutes back
        log_filename: For load mode - specific file to load
        max_traces: Limit number of traces to process (None = all)
    """
    print("🚀 Starting Log Analysis Pipeline\n")
    
    # Step 1: Get logs
    log_data = get_logs(mode=mode, time_range_minutes=time_range_minutes, log_filename=log_filename)
    
    if not log_data or not log_data.get("traces"):
        print("❌ No logs available to analyze")
        return
    
    print(f"\n📊 Summary:")
    print(f"   Total traces: {log_data['total_traces']}")
    print(f"   Total logs: {log_data['total_logs']}")
    print(f"   Fetch time: {log_data['fetch_time']}")
    
    # Step 2: Process each trace
    traces = log_data["traces"]
    
    if max_traces:
        traces = dict(list(traces.items())[:max_traces])
        print(f"   Processing first {len(traces)} traces only")
    
    results = []
    for i, (trace_id, logs) in enumerate(traces.items(), 1):
        print(f"\n[{i}/{len(traces)}]")
        analysis = process_trace(trace_id, logs)
        
        if analysis:
            results.append({
                "trace_id": trace_id,
                "cause": analysis.get("cause"),
                "category": analysis.get("category"),
                "confidence": analysis.get("confidence")
            })
        
        # Small delay to avoid rate limits
        if i < len(traces):
            time.sleep(1)
    
    # Step 3: Final summary
    print("\n" + "="*80)
    print("📈 PIPELINE SUMMARY")
    print("="*80)
    print(f"✅ Processed: {len(results)}/{len(traces)} traces")
    
    if results:
        print("\nResults:")
        for r in results:
            print(f"  🧵 {r['trace_id'][:30]}... → {r['category']} ({r['confidence']}%)")
    
    print("\n✅ Pipeline complete!")

# agent.py - Add this function at the end (keep everything else same)

# ... (all your existing code stays the same) ...

# Add this new function:
def run_analysis_for_api(time_range_minutes=60, max_traces=10):
    """
    Wrapper function for API to call
    Returns analysis results instead of just printing
    """
    print("🚀 Starting Log Analysis Pipeline\n")
    
    # Step 1: Get logs
    log_data = get_logs(mode="fetch", time_range_minutes=time_range_minutes)
    
    if not log_data or not log_data.get("traces"):
        return {
            "status": "success",
            "message": "No logs available",
            "total_traces": 0,
            "analyzed_traces": 0,
            "results": []
        }
    
    print(f"\n📊 Summary:")
    print(f"   Total traces: {log_data['total_traces']}")
    print(f"   Total logs: {log_data['total_logs']}")
    
    # Step 2: Process each trace
    traces = log_data["traces"]
    
    if max_traces:
        traces = dict(list(traces.items())[:max_traces])
        print(f"   Processing first {len(traces)} traces only")
    
    results = []
    for i, (trace_id, logs) in enumerate(traces.items(), 1):
        print(f"\n[{i}/{len(traces)}] Processing trace {trace_id[:20]}...")
        
        # Prepare log summary for Gemini
        log_summary = {
            "trace_id": trace_id,
            "log_count": len(logs),
            "logs": []
        }
        
        for log in logs:
            log_summary["logs"].append({
                "timestamp": log["timestamp"],
                "severity": log["severity"],
                "service": log["service"],
                "message": log["message"],
                "root_cause": log.get("root_cause"),
                "suggestion": log.get("suggestion")
            })
        
        # Get AI Analysis
        analysis = analyze_logs(log_summary)
        
        if analysis:
            print(f"✅ Analysis complete for trace {trace_id[:20]}")
            
            # Push to Firebase
            if db:
                try:
                    doc_ref = db.collection("incidents").add({
                        "trace_id": trace_id,
                        "timestamp": datetime.now().isoformat(),
                        "service": logs[0]["service"] if logs else "unknown",
                        "log_count": len(logs),
                        "first_seen": logs[0]["timestamp"] if logs else None,
                        "last_seen": logs[-1]["timestamp"] if logs else None,
                        "analysis": analysis,
                        "status": "AUTO-RESOLVED" if analysis.get('confidence', 0) > 0.8 else "PENDING_REVIEW",
                        "raw_logs": log_summary["logs"]
                    })
                except Exception as e:
                    print(f"❌ Failed to update Firebase: {e}")
            
            results.append({
                "trace_id": trace_id,
                "root_cause": analysis.get("cause", "Unknown"),
                "category": analysis.get("category", "Unknown"),
                "action": analysis.get("action", "No action"),
                "confidence": float(analysis.get("confidence", 0)) if isinstance(analysis.get("confidence"), (int, float)) else 0.0,
                "log_count": len(logs)
            })
        
        time.sleep(1)  # Rate limit protection
    
    print(f"\n✅ Analysis complete! Processed {len(results)}/{len(traces)} traces")
    
    return {
        "status": "success",
        "message": f"Analyzed {len(results)} traces",
        "total_traces": len(traces),
        "analyzed_traces": len(results),
        "results": results
    }


# Keep existing main block
if __name__ == "__main__":
    run_prototype(mode="fetch", time_range_minutes=60, max_traces=5)

# # --- 7. EXAMPLE USAGE ---
# if __name__ == "__main__":
#     # Option 1: Fetch new logs from GCP and analyze (last 60 minutes)
#     run_prototype(mode="fetch", time_range_minutes=60, max_traces=5)
    
#     # Option 2: Fetch logs from last 2 hours
#     # run_prototype(mode="fetch", time_range_minutes=120)
    
#     # Option 3: Load from saved file (most recent)
#     # run_prototype(mode="load")
    
#     # Option 4: Load specific saved file
#     # run_prototype(mode="load", log_filename="logs_20260108_091500.json")
    
#     # Option 5: Fetch and process ALL traces (no limit)
#     # run_prototype(mode="fetch", time_range_minutes=60, max_traces=None)
