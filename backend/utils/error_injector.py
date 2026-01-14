import json
import time
import random
from datetime import datetime

# A collection of diverse Cloud Run "Disaster Scenarios"
SCENARIOS = [
    {
        "name": "Database Config Missing",
        "payload": "KeyError: 'DATABASE_URL' not found in environment. Process exited with code 1"
    },
    {
        "name": "IAM Permission Failure",
        "payload": "google.api_core.exceptions.Forbidden: 403 Caller does not have storage.objects.get access to the bucket."
    },
    {
        "name": "Out of Memory (OOM)",
        "payload": "Memory limit of 512 MiB exceeded with 513 MiB used. Revision terminated."
    },
    {
        "name": "Service Timeout",
        "payload": "The request has been terminated because it has reached the maximum request timeout of 60s."
    },
    {
        "name": "Broken Deployment (ImportError)",
        "payload": "ImportError: cannot import name 'get_db_connection' from 'utils' (/app/utils.py)"
    }
]

def inject_error():
    # Pick a random failure
    scenario = random.choice(SCENARIOS)
    
    mock_entry = [{
        "timestamp": datetime.now().isoformat() + "Z",
        "severity": "ERROR",
        "resource": {
            "type": "cloud_run_revision",
            "labels": { "service_name": "payment-api", "location": "us-central1" }
        },
        "textPayload": scenario['payload']
    }]

    # Overwrite the mock file
    with open("data/mock_logs.json", "w") as f:
        json.dump(mock_entry, f, indent=2)
    
    print(f"INJECTED ERROR: {scenario['name']}")

if __name__ == "__main__":
    while True:
        inject_error()
        print("Waiting 15 seconds for Agent to detect...")
        time.sleep(15)
        
        
        







