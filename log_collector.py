# log_collector.py - Fetches logs from GCP and saves to data/ folder
import json
import re
import os
from datetime import datetime, timedelta
from collections import defaultdict
from google.cloud import logging_v2
from google_auth_oauthlib.flow import InstalledAppFlow

PROJECT_ID = "project-e2bcb697-e160-439a-a3c"
SERVICE_NAME = "cloud-rca-service"

SCOPES = [
    "https://www.googleapis.com/auth/logging.read",
    "https://www.googleapis.com/auth/cloud-platform.read-only",
]

# Data directory for storing logs
DATA_DIR = "data"


def authenticate():
    """OAuth authentication for user credentials"""
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
    )
    return flow.run_local_server(port=0)


def parse_log_entry(entry):
    """
    Parse Cloud Run logs with format:
    ERROR:cloud-rca:{"trace_id": "...", "message": "...", ...}
    
    Extracts severity from the TEXT PREFIX, not from GCP system severity
    """
    payload = entry.payload
    
    if not isinstance(payload, str):
        return None
    
    # Extract JSON from textPayload (after the prefix)
    # Pattern: ERROR:cloud-rca:{...} or WARNING:cloud-rca:{...}
    match = re.search(r'(ERROR|WARNING|INFO|CRITICAL):cloud-rca:(\{.+\})', payload)
    
    if not match:
        return None
    
    log_level = match.group(1)  # ERROR, WARNING, INFO - from TEXT, not system
    json_str = match.group(2)
    
    try:
        log_data = json.loads(json_str)
    except json.JSONDecodeError:
        return None
    
    trace_id = log_data.get("trace_id")
    if not trace_id:
        return None
    
    return {
        "trace_id": trace_id,
        "message": log_data.get("message"),
        "service": log_data.get("service"),
        "root_cause": log_data.get("root_cause"),
        "suggestion": log_data.get("suggestion"),
        "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
        "severity": log_level,  # ✅ Use the actual log level from the TEXT
        "log_name": entry.log_name,
        "resource_labels": dict(entry.resource.labels) if entry.resource else {},
    }


def save_logs_to_json(traces, filename=None):
    """
    Save logs to JSON file in data/ folder
    
    Args:
        traces: Dictionary of traces with logs
        filename: Custom filename (optional). If None, generates timestamp-based name
    
    Returns:
        Path to saved file
    """
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs_{timestamp}.json"
    
    # Ensure .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    filepath = os.path.join(DATA_DIR, filename)
    
    # Prepare data for saving with severity counts per trace
    traces_with_metadata = {}
    
    for trace_id, logs in traces.items():
        # Count severities based on TEXT-EXTRACTED severity
        severity_counts = {
            "ERROR": sum(1 for log in logs if log["severity"] == "ERROR"),
            "WARNING": sum(1 for log in logs if log["severity"] == "WARNING"),
            "INFO": sum(1 for log in logs if log["severity"] == "INFO"),
            "CRITICAL": sum(1 for log in logs if log["severity"] == "CRITICAL"),
        }
        
        traces_with_metadata[trace_id] = {
            "log_count": len(logs),
            "severity_counts": severity_counts,
            "has_errors": severity_counts["ERROR"] > 0 or severity_counts["CRITICAL"] > 0,
            "first_seen": logs[0]["timestamp"] if logs else None,
            "last_seen": logs[-1]["timestamp"] if logs else None,
            "logs": logs
        }
    
    output_data = {
        "fetch_time": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "service_name": SERVICE_NAME,
        "total_traces": len(traces),
        "total_logs": sum(len(logs) for logs in traces.values()),
        "traces": traces_with_metadata
    }
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved logs to: {filepath}")
    return filepath


def fetch_logs(creds, time_range_minutes=60, save_to_file=True, filename=None):
    """
    Fetch logs from Cloud Run for given time range
    
    Args:
        creds: OAuth credentials
        time_range_minutes: How many minutes back to fetch logs
        save_to_file: Whether to save logs to JSON file (default: True)
        filename: Custom filename for saving (optional)
    
    Returns:
        Dictionary of log entries grouped by trace_id
    """
    client = logging_v2.Client(project=PROJECT_ID, credentials=creds)
    
    # Time filter for recent logs
    start_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
    timestamp_filter = f'timestamp >= "{start_time.isoformat()}Z"'
    
    log_filter = f'''
        resource.type="cloud_run_revision"
        resource.labels.service_name="{SERVICE_NAME}"
        (logName="projects/{PROJECT_ID}/logs/run.googleapis.com%2Fstderr"
         OR logName="projects/{PROJECT_ID}/logs/run.googleapis.com%2Fstdout")
        {timestamp_filter}
    '''
    
    entries_iter = client.list_entries(
        filter_=log_filter,
        order_by=logging_v2.DESCENDING,
        page_size=1000,
    )
    
    traces = defaultdict(list)
    count_entries = 0
    count_parsed = 0
    
    for entry in entries_iter:
        count_entries += 1
        parsed = parse_log_entry(entry)
        if parsed and parsed["trace_id"]:
            count_parsed += 1
            traces[parsed["trace_id"]].append(parsed)
    
    # Sort logs within each trace by timestamp
    for trace_id in traces:
        traces[trace_id].sort(key=lambda x: x["timestamp"])
    
    traces_dict = dict(traces)
    
    print(f"✅ Fetched {count_parsed} logs across {len(traces_dict)} traces")
    print(f"   (Raw entries: {count_entries} | Parsed: {count_parsed})")
    
    # Save to file if requested
    if save_to_file:
        save_logs_to_json(traces_dict, filename)
    
    return traces_dict


def load_logs_from_json(filename):
    """
    Load logs from a JSON file in data/ folder
    
    Args:
        filename: Name of the file to load
    
    Returns:
        Dictionary with log data
    """
    filepath = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Log file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📂 Loaded logs from: {filepath}")
    print(f"   Total traces: {data['total_traces']}")
    print(f"   Total logs: {data['total_logs']}")
    
    return data


def list_saved_logs():
    """List all saved log files in data/ folder"""
    if not os.path.exists(DATA_DIR):
        print(f"⚠️ No data directory found")
        return []
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    
    if not files:
        print(f"⚠️ No log files found in {DATA_DIR}/")
        return []
    
    print(f"📁 Found {len(files)} log file(s) in {DATA_DIR}/:")
    for f in sorted(files):
        filepath = os.path.join(DATA_DIR, f)
        size = os.path.getsize(filepath)
        print(f"   - {f} ({size:,} bytes)")
    
    return files


def display_logs_formatted(traces):
    """Display logs in beautiful formatted output"""
    for trace_id, logs in traces.items():
        print("═" * 80)
        print(f"🧵 TRACE ID: {trace_id}")
        print(f"📝 {len(logs)} log entries")
        print("═" * 80)
        
        for log in logs:
            severity_emoji = {
                "ERROR": "❌",
                "WARNING": "⚠️",
                "INFO": "ℹ️",
                "CRITICAL": "🔥"
            }.get(log["severity"], "📄")
            
            print(f"\n{severity_emoji} [{log['severity']}] {log['timestamp']}")
            print(f"   Service: {log['service']}")
            print(f"   Message: {log['message']}")
            
            if log.get("root_cause"):
                print(f"   🔍 Root Cause: {log['root_cause']}")
            if log.get("suggestion"):
                print(f"   💡 Suggestion: {log['suggestion']}")
        
        print()


# Example usage
if __name__ == "__main__":
    # Fetch and save logs
    creds = authenticate()
    traces = fetch_logs(creds, time_range_minutes=120)
    
    # Display formatted output
    display_logs_formatted(traces)
    
    print(f"✅ Collected {len(traces)} request traces")
    
    # List all saved files
    print("\n" + "="*80)
    list_saved_logs()
