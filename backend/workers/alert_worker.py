import os
import sys
import asyncio
from datetime import datetime

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import db
from services.email_service import email_service
from google.cloud.firestore_v1.base_query import FieldFilter

class AlertWorker:
    def __init__(self):
        self.db = db
        self.running = False
        self._thread = None
        self.processed_incidents = set()

    async def start(self):
        if self.running:
            return
        self.running = True
        # Create background task
        asyncio.create_task(self._run_loop())
        print("🤖 Alert Worker started. Monitoring incidents...")

    async def stop(self):
        self.running = False
        print("🤖 Alert Worker stopped.")

    async def _run_loop(self):
        while self.running:
            try:
                await self._check_and_trigger_alerts()
            except Exception as e:
                print(f"❌ Alert Worker Error: {e}")
            await asyncio.sleep(10) # Check every 10 seconds

    async def _check_and_trigger_alerts(self):
        if not self.db:
            return

        # 1. Fetch active alert rules
        rules_docs = await self.db.collection("alert_rules").where(filter=FieldFilter("enabled", "==", True)).get()
        rules = [d.to_dict() for d in rules_docs]
        if not rules:
            return

        # 2. Fetch recent incidents (last 5 minutes)
        # For simplicity in this demo, we'll just track seen IDs in memory
        incidents_docs = await self.db.collection("incidents").order_by("timestamp", direction="DESCENDING").limit(20).get()
        
        for doc in incidents_docs:
            incident = doc.to_dict()
            incident_id = doc.id
            
            if incident_id in self.processed_incidents:
                continue
            
            # Match against rules
            category = incident.get('analysis', {}).get('category', 'unknown')
            
            for rule in rules:
                if rule.get('category').lower() == category.lower():
                    print(f"🎯 ALERT MATCH: Incident {incident_id} matches rule '{rule['name']}' (Category: {category})")
                    
                    # Send alert to a default recipient or user who created the rule
                    # In a real app, we'd look up the user's email. For now using GMAIL_USER as recipient.
                    recipient = os.getenv("GMAIL_USER")
                    if recipient:
                        await email_service.send_alert_email(
                            recipient, 
                            rule['name'], 
                            {
                                'trace_id': incident.get('trace_id'),
                                'category': category,
                                'priority': incident.get('priority'),
                                'redacted_text': incident.get('redacted_text')
                            }
                        )
            
            self.processed_incidents.add(incident_id)

# Singleton instance
alert_worker = AlertWorker()

if __name__ == "__main__":
    # Test runner
    worker = AlertWorker()
    worker._run_loop()
