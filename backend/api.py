from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os

# Import the agent logic
try:
    from agent import run_analysis_for_api, db
except ImportError:
    print("❌ Critical Error: Could not find agent.py. Ensure both files are in the same directory.")

app = FastAPI(title="Cloud RCA - Self-Healing Dashboard")

# --- DATA MODELS ---
class AnalyzeRequest(BaseModel):
    time_range_minutes: int = 60
    max_traces: Optional[int] = 10

# --- MODULAR API ENDPOINTS (The "Action" Layer) ---

@app.post("/api/analyze")
async def analyze_logs_endpoint(request: AnalyzeRequest):
    """Triggers the full Gemini-3 AI analysis pipeline."""
    try:
        result = run_analysis_for_api(
            time_range_minutes=request.time_range_minutes,
            max_traces=request.max_traces
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/incident/{trace_id}/root-cause")
async def get_root_cause(trace_id: str):
    """Retrieves actual AI reasoning from Firebase."""
    try:
        # Search Firebase for the document matching this trace_id
        docs = db.collection("incidents").where("trace_id", "==", trace_id).limit(1).get()
        
        if not docs:
            raise HTTPException(status_code=404, detail="Incident not found in database.")
        
        # Extract the data from the first matching document
        data = docs[0].to_dict()
        
        return {
            "trace_id": trace_id,
            "status": "Success",
            "root_cause": data.get("analysis", {}).get("cause"),
            "category": data.get("analysis", {}).get("category"),
            "confidence": data.get("analysis", {}).get("confidence")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@app.get("/api/incident/{trace_id}/suggestions")
async def get_suggestions(trace_id: str):
    """Retrieves AI-generated remediation commands from Firebase."""
    try:
        # Search Firestore for the record
        docs = db.collection("incidents").where("trace_id", "==", trace_id).limit(1).get()
        
        if not docs:
            raise HTTPException(status_code=404, detail="Incident ID not found.")
        
        data = docs[0].to_dict()
        
        return {
            "trace_id": trace_id,
            "status": "Success",
            "remediation_steps": data.get("analysis", {}).get("action"),
            "priority_level": data.get("priority", "P2"),
            "auto_healing_status": "Eligible" if data.get("analysis", {}).get("confidence", 0) > 0.8 else "Review Required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Query Failed: {str(e)}")

@app.get("/api/incident/{trace_id}/impact")
async def get_impact(trace_id: str):
    """Retrieves Business Impact, Correlation, and Security Alerts."""
    try:
        docs = db.collection("incidents").where("trace_id", "==", trace_id).limit(1).get()
        
        if not docs:
            raise HTTPException(status_code=404, detail="Incident ID not found.")
            
        data = docs[0].to_dict()
        
        return {
            "trace_id": trace_id,
            "priority": data.get("priority"),
            "correlation_insight": data.get("correlation"),
            "security_breach_detected": data.get("security_alert", False),
            "occurrence_count": data.get("occurrence_count", 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cloud RCA | Autonomous Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .alert-p0 { animation: pulse-bg 2s infinite; }
        @keyframes pulse-bg {
            0% { background-color: #ef4444; }
            50% { background-color: #b91c1c; }
            100% { background-color: #ef4444; }
        }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">
    <nav class="bg-slate-900 text-white p-6 shadow-2xl">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-black italic tracking-tighter">🛡️ CLOUD-RCA <span class="text-indigo-400">AGENT</span></h1>
            <div id="securityStatus" class="hidden px-4 py-2 bg-red-600 rounded-lg text-xs font-bold animate-bounce">
                🚨 SECURITY SHIELD ACTIVE
            </div>
        </div>
    </nav>

    <div class="container mx-auto px-6 py-10 max-w-5xl">
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 mb-10 flex gap-6 items-end">
            <div class="flex-1">
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-2">Analysis Window (Min)</label>
                <input type="number" id="timeRange" value="60" class="w-full border-2 border-slate-100 p-3 rounded-xl font-bold">
            </div>
            <button onclick="runAnalysis()" id="btn" class="bg-indigo-600 text-white px-10 py-4 rounded-xl font-black hover:bg-indigo-700 transition-all shadow-xl shadow-indigo-100">
                START AI ANALYSIS
            </button>
        </div>

        <div id="loader" class="hidden text-center py-20">
            <div class="text-4xl animate-spin mb-4">⚙️</div>
            <p class="font-bold text-slate-600 uppercase tracking-widest text-xs">Gemini is correlating traces...</p>
        </div>

        <div id="results" class="space-y-10"></div>
    </div>

    <script>
        async function runAnalysis() {
            const btn = document.getElementById('btn');
            const loader = document.getElementById('loader');
            const resultsDiv = document.getElementById('results');
            
            btn.disabled = true;
            loader.classList.remove('hidden');
            resultsDiv.innerHTML = '';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ time_range_minutes: document.getElementById('timeRange').value })
                });
                const data = await response.json();
                render(data.results);
            } catch (e) {
                alert("API Connection Failed");
            } finally {
                btn.disabled = false;
                loader.classList.add('hidden');
            }
        }

        function render(incidents) {
            const resultsDiv = document.getElementById('results');
            const secBadge = document.getElementById('securityStatus');

            if(!incidents || incidents.length === 0) {
                resultsDiv.innerHTML = "<p class='text-center text-slate-400'>No anomalies detected.</p>";
                return;
            }

            resultsDiv.innerHTML = incidents.map(res => {
                const isP0 = res.priority && res.priority.includes('P0');
                if(res.security_alert) secBadge.classList.remove('hidden');

                return `
                <div class="bg-white rounded-[2.5rem] shadow-2xl overflow-hidden border border-slate-100">
                    <div class="p-6 ${isP0 ? 'alert-p0 text-white' : 'bg-slate-900 text-white'} flex justify-between items-center">
                        <div>
                            <p class="text-[10px] font-black uppercase opacity-60">Status Escalation</p>
                            <h2 class="text-2xl font-black">${res.priority || 'P2'} INCIDENT</h2>
                        </div>
                        <div class="text-right">
                            <p class="text-[10px] font-black opacity-60 tracking-widest">TRACE_ID</p>
                            <p class="font-mono text-sm">${res.trace_id}</p>
                        </div>
                    </div>

                    <div class="p-10">
                        <div class="bg-indigo-50 border-2 border-indigo-100 p-6 rounded-3xl mb-8 flex gap-6 items-center">
                            <div class="text-3xl">🔗</div>
                            <div>
                                <h4 class="text-indigo-900 font-black text-xs uppercase mb-1">AI Correlation Insight</h4>
                                <p class="text-indigo-800 font-medium italic">"${res.correlation}"</p>
                            </div>
                        </div>

                        <div class="grid md:grid-cols-2 gap-10">
                            <div class="space-y-8">
                                <div>
                                    <h4 class="text-slate-400 font-black text-[10px] uppercase mb-2">Root Cause Analysis</h4>
                                    <p class="text-slate-900 font-bold text-xl leading-tight">${res.root_cause}</p>
                                </div>
                                <div class="bg-emerald-50 border-l-8 border-emerald-500 p-6 rounded-r-2xl">
                                    <h4 class="text-emerald-700 font-black text-[10px] uppercase mb-2">Remediation Action</h4>
                                    <p class="text-emerald-900 font-black">${res.action}</p>
                                </div>
                            </div>

                            <div class="bg-slate-900 rounded-3xl p-8 shadow-inner relative">
                                <div class="absolute top-4 right-6 text-[10px] font-black text-slate-500">PII SHIELD ACTIVE</div>
                                <h4 class="text-slate-500 font-black text-[10px] uppercase mb-4 tracking-widest">Sanitized Logs</h4>
                                <div class="font-mono text-sm text-blue-300 leading-relaxed">
                                    ${res.redacted_text}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                `;
            }).join('');
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTML_DASHBOARD

if __name__ == "__main__":
    print("🚀 Self-Healing Dashboard starting on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)