from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import sys

# Import the agent
from agent import run_analysis_for_api

app = FastAPI(title="Cloud RCA Dashboard")

# --- MODELS ---
class AnalyzeRequest(BaseModel):
    time_range_minutes: int = 60
    max_traces: Optional[int] = 10

# --- UPDATED HTML DASHBOARD ---
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud RCA - Intelligent Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .slide-in { animation: slideIn 0.4s ease-out forwards; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .blur-text { filter: blur(4px); transition: filter 0.3s; cursor: help; }
        .blur-text:hover { filter: blur(0); }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">
    
    <div class="bg-slate-900 text-white shadow-xl">
        <div class="container mx-auto px-6 py-6 max-w-7xl flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-extrabold flex items-center gap-3">
                    <span class="text-4xl">🛡️</span> Cloud RCA Agent
                </h1>
                <p class="text-slate-400">Security-First Autonomous Reliability Hub</p>
            </div>
            <div class="flex gap-4">
                <div id="statsPII" class="bg-red-500/10 border border-red-500/50 px-4 py-2 rounded-lg text-red-400 text-sm font-bold hidden">
                    🚨 PII Blocked
                </div>
            </div>
        </div>
    </div>

    <div class="container mx-auto px-6 py-8 max-w-7xl">
        <div class="bg-white rounded-xl shadow-sm p-6 mb-8 border border-slate-200">
            <div class="grid md:grid-cols-3 gap-6">
                <div>
                    <label class="block text-xs font-bold uppercase text-slate-500 mb-2">Time Range (Min)</label>
                    <input type="number" id="timeRange" value="60" class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold uppercase text-slate-500 mb-2">Max Traces</label>
                    <input type="number" id="maxTraces" value="10" class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div class="flex items-end">
                    <button onclick="analyzeLog()" id="analyzeBtn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 rounded-lg transition-all shadow-lg shadow-indigo-200">
                        🚀 Run Deep Analysis
                    </button>
                </div>
            </div>
        </div>

        <div id="resultsSection" class="hidden">
            <div id="resultsContainer" class="grid grid-cols-1 gap-6"></div>
        </div>

        <div id="loadingIndicator" class="hidden text-center py-20">
            <div class="animate-spin text-5xl mb-4">⚙️</div>
            <p class="text-slate-600 font-medium italic">Gemini is correlating patterns and scrubbing PII...</p>
        </div>
    </div>

    <script>
        async function analyzeLog() {
            const btn = document.getElementById('analyzeBtn');
            const loader = document.getElementById('loadingIndicator');
            const container = document.getElementById('resultsContainer');
            const section = document.getElementById('resultsSection');

            loader.classList.remove('hidden');
            section.classList.add('hidden');
            btn.disabled = true;

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        time_range_minutes: parseInt(document.getElementById('timeRange').value),
                        max_traces: parseInt(document.getElementById('maxTraces').value)
                    })
                });
                const data = await response.json();
                renderResults(data.results);
            } catch (e) {
                alert("Analysis Error: " + e);
            } finally {
                loader.classList.add('hidden');
                section.classList.remove('hidden');
                btn.disabled = false;
            }
        }

        function renderResults(results) {
    const container = document.getElementById('resultsContainer');
    const statsPII = document.getElementById('statsPII');
    
    if (!results || results.length === 0) {
        container.innerHTML = "<div class='text-center py-20 text-slate-400'>✅ Systems Operational</div>";
        return;
    }

    // Sort to put P0 at the very top
    results.sort((a, b) => (a.priority.includes('P0') ? -1 : 1));

    container.innerHTML = results.map((res) => {
        const isCritical = res.priority && res.priority.includes('P0');
        
        // Show Global PII Alert Badge if security_alert is true
        if (res.security_alert) statsPII.classList.remove('hidden');

        return `
        ${isCritical ? `
        <div class="bg-red-600 text-white p-4 rounded-t-2xl flex items-center gap-4 animate-pulse border-b-4 border-red-800">
            <span class="text-2xl">🚨</span>
            <div class="flex-1">
                <p class="text-xs font-black uppercase tracking-widest opacity-80">Critical System Escalation</p>
                <p class="text-lg font-bold">Priority ${res.priority}: Immediate Action Required</p>
            </div>
            <div class="text-xs font-mono bg-black/20 px-2 py-1 rounded">TR-ID: ${res.trace_id}</div>
        </div>
        ` : ''}

        <div class="bg-white border-x border-b border-slate-200 ${isCritical ? 'rounded-b-2xl' : 'rounded-2xl'} shadow-2xl mb-10 overflow-hidden">
            
            <div class="p-6">
                <div class="flex items-start gap-4 p-5 bg-indigo-50 rounded-2xl border-2 border-indigo-100 mb-6">
                    <div class="bg-indigo-600 text-white p-3 rounded-xl text-xl">🔗</div>
                    <div>
                        <h4 class="text-indigo-900 font-black text-xs uppercase tracking-tighter">AI Correlation Alert</h4>
                        <p class="text-indigo-800 text-md leading-relaxed mt-1 italic font-medium">
                            "${res.correlation}"
                        </p>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-8">
                    <div class="space-y-6">
                        <div class="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                            <h4 class="text-slate-400 font-bold text-[10px] uppercase mb-2">Root Cause Analysis</h4>
                            <p class="text-slate-800 font-semibold text-lg">${res.root_cause}</p>
                        </div>
                        <div class="bg-emerald-50 p-5 rounded-2xl border border-emerald-100">
                            <h4 class="text-emerald-600 font-bold text-[10px] uppercase mb-2">AI Suggested Remediation</h4>
                            <p class="text-emerald-900 font-black">${res.action}</p>
                        </div>
                    </div>

                    <div class="bg-slate-900 rounded-2xl p-6 relative">
                         <div class="absolute top-4 right-4 flex gap-2">
                            ${res.security_alert ? '<span class="bg-red-500 text-[10px] text-white px-2 py-1 rounded font-black shadow-lg">🛡️ SHIELD ACTIVE</span>' : ''}
                         </div>
                        <h4 class="text-slate-500 font-bold text-[10px] uppercase mb-4">Redacted Intelligence Summary</h4>
                        <div class="font-mono text-sm text-blue-300 whitespace-pre-line leading-relaxed">
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

# --- API ENDPOINTS ---

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTML_DASHBOARD

@app.post("/api/analyze")
async def analyze_logs_endpoint(request: AnalyzeRequest):
    try:
        # result = { "results": [ { "priority": "P0", "correlation": "...", "security_alert": True, ... } ] }
        result = run_analysis_for_api(
            time_range_minutes=request.time_range_minutes,
            max_traces=request.max_traces
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 DASHBOARD STARTING...")
    # Using 127.0.0.1 is often more stable for local testing
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")