import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { analyticsAPI, groupsAPI, analysisAPI } from '../services/api';
import { ERROR_CATEGORIES } from '../constants/errorCategories';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import SystemIntelligencePanel from '../components/cards/SystemIntelligencePanel';
import IncidentCanvasCard from '../components/cards/IncidentCanvasCard';
import DeepDivePanel from '../components/panels/DeepDivePanel'; // Reuse for dashboard interactions

const DashboardPage = () => {
    const navigate = useNavigate();
    // State for dashboard data
    const [metrics, setMetrics] = useState({
        totalErrors: 0,
        activeGroups: 0,
        criticalIssues: 0,
        healthScore: 100,
        avgConfidence: 0,
        impactedServices: 0
    });
    const [recentGroups, setRecentGroups] = useState([]);
    const [categoryFilter, setCategoryFilter] = useState('All');
    const [loadingData, setLoadingData] = useState(true);
    const [selectedGroup, setSelectedGroup] = useState(null); // For Deep Dive

    // State for Analysis Form
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisStatus, setAnalysisStatus] = useState(null);
    const [analysisConfig, setAnalysisConfig] = useState({
        time_range_minutes: 60,
        max_traces: 10
    });
    const [analysisResults, setAnalysisResults] = useState(null);

    // Fetch Dashboard Data function
    const fetchDashboardData = async (showLoading = true) => {
        try {
            if (showLoading) setLoadingData(true);

            const [statsRes, groupsRes] = await Promise.allSettled([
                analyticsAPI.summary(),
                groupsAPI.list({
                    status: 'active',
                    limit: 10,
                    ...(categoryFilter !== 'All' && { category: categoryFilter })
                })
            ]);

            // Handle Stats
            if (statsRes.status === 'fulfilled') {
                setMetrics(statsRes.value.data);
            } else {
                console.error("Failed to load analytics:", statsRes.reason);
            }

            // Handle Groups
            if (groupsRes.status === 'fulfilled') {
                setRecentGroups(groupsRes.value.data);
            } else {
                console.error("Failed to load groups:", groupsRes.reason);
            }

        } catch (err) {
            console.error("Dashboard Load Error:", err);
        } finally {
            if (showLoading) setLoadingData(false);
        }
    };

    // Initial load and filter changes
    useEffect(() => {
        fetchDashboardData();
    }, [categoryFilter]);

    // Handle Analysis Trigger
    const handleStartAnalysis = async (e) => {
        e.preventDefault();
        setIsAnalyzing(true);
        setAnalysisStatus("Initiating Deep Scan...");

        try {
            console.log('📡 Starting analysis with config:', analysisConfig);
            const res = await analysisAPI.start(analysisConfig);

            if (res.data.results) {
                console.log('✅ Analysis complete! Results:', res.data.results);
                setAnalysisResults(res.data.results);
                setAnalysisStatus("Insights Generated.");

                // Still refresh background metrics, but don't wait for it
                fetchDashboardData(false);

                setTimeout(() => {
                    setIsAnalyzing(false);
                    setAnalysisStatus(null);
                }, 2000);
            } else {
                throw new Error("No results returned from analysis");
            }
        } catch (err) {
            console.error("❌ Analysis failed:", err);
            setIsAnalyzing(false);
            setAnalysisStatus("Analysis Failed: " + (err.response?.data?.detail || err.message));
            setTimeout(() => setAnalysisStatus(null), 5000);
        }
    };

    if (loadingData) return <LoadingSpinner size="lg" className="min-h-[50vh]" />;

    return (
        <div className="space-y-8">
            {/* Header / Global Context */}
            <div className="flex justify-between items-end border-b border-white/10 pb-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-100 tracking-tight">Mission Control</h1>
                    <p className="text-sm text-gray-500 font-mono mt-1">System Status: <span className="text-success-green">NOMINAL</span></p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <label className="text-xs font-mono text-gray-500 uppercase">Category:</label>
                        <select
                            value={categoryFilter}
                            onChange={(e) => setCategoryFilter(e.target.value)}
                            className="bg-black/40 border border-white/10 rounded px-2 py-1 text-xs font-mono text-gray-300 focus:border-electric-blue outline-none"
                        >
                            <option value="All">All</option>
                            {ERROR_CATEGORIES.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>
                    <div className="bg-black/20 px-3 py-1 rounded text-xs font-mono text-gray-500 border border-white/5">
                        REGION: US-EAST-1
                    </div>
                </div>
            </div>

            {/* System Intelligence Panels (Top Row) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <SystemIntelligencePanel
                    title="AI Confidence (Avg)"
                    value={`${metrics.avgConfidence}%`}
                    icon="trending-up"
                    color="blue"
                    subtext="Based on last 50 analyses"
                />
                <SystemIntelligencePanel
                    title="System Health"
                    value={`${metrics.healthScore}/100`}
                    icon="collection"
                    color="indigo"
                    subtext={`${metrics.activeGroups} active anomalies`}
                />
                <SystemIntelligencePanel
                    title="Critical Events"
                    value={metrics.criticalIssues}
                    icon="exclamation"
                    color="red"
                    subtext={`Across ${metrics.impactedServices} service`}
                />
            </div>

            {/* Centered Analysis Section */}
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Analysis Controller */}
                <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-8 shadow-2xl relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-br from-electric-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>

                    <div className="relative z-10 text-center mb-8">
                        <h2 className="text-xl font-bold text-white tracking-wide uppercase">AI Deep Scan Engine</h2>
                        <p className="text-gray-500 text-sm mt-2">Trigger a comprehensive Gemini-3 analysis across your cloud traces</p>
                    </div>

                    <form onSubmit={handleStartAnalysis} className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
                        <div className="space-y-2">
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Lookback Period</label>
                            <select
                                className="w-full bg-black/60 border border-white/10 rounded-xl text-gray-200 text-sm py-3 px-4 focus:border-electric-blue focus:ring-1 focus:ring-electric-blue outline-none transition-all"
                                value={analysisConfig.time_range_minutes}
                                onChange={(e) => setAnalysisConfig({ ...analysisConfig, time_range_minutes: parseInt(e.target.value) })}
                                disabled={isAnalyzing}
                            >
                                <option value={60}>Last 1 Hour</option>
                                <option value={360}>Last 6 Hours</option>
                                <option value={1440}>Last 24 Hours</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Trace Capacity</label>
                            <input
                                type="number"
                                className="w-full bg-black/60 border border-white/10 rounded-xl text-gray-200 text-sm py-3 px-4 focus:border-electric-blue outline-none transition-all"
                                value={analysisConfig.max_traces}
                                onChange={(e) => setAnalysisConfig({ ...analysisConfig, max_traces: parseInt(e.target.value) || 0 })}
                                min="10"
                                max="1000"
                                disabled={isAnalyzing}
                            />
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={isAnalyzing}
                                className={`w-full py-3.5 px-6 rounded-xl text-sm font-black tracking-widest transition-all uppercase
                                    ${isAnalyzing
                                        ? 'bg-gray-800 text-gray-400 cursor-wait'
                                        : 'bg-electric-blue text-black hover:bg-white hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_30px_rgba(0,209,255,0.2)]'
                                    }
                                `}
                            >
                                {isAnalyzing ? 'Scanning...' : 'Run Analysis'}
                            </button>
                        </div>
                    </form>

                    {analysisStatus && (
                        <div className="mt-8 p-4 bg-electric-blue/5 rounded-xl border border-electric-blue/20 text-xs font-mono text-center text-electric-blue tracking-tighter animate-pulse">
                            &gt; {analysisStatus}
                        </div>
                    )}
                </div>

                {/* Results Display Area */}
                <div className="space-y-6">
                    <div className="flex items-center gap-4">
                        <div className="h-[1px] flex-1 bg-white/10"></div>
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500">Analysis Output</h3>
                        <div className="h-[1px] flex-1 bg-white/10"></div>
                    </div>

                    {!analysisResults && !isAnalyzing && (
                        <div className="py-20 text-center border-2 border-dashed border-white/5 rounded-3xl">
                            <div className="opacity-20 grayscale mb-4">📡</div>
                            <p className="text-gray-600 text-sm font-mono uppercase tracking-widest">No active session. Run a scan to generate insights.</p>
                        </div>
                    )}

                    {isAnalyzing && (
                        <div className="py-20 flex flex-col items-center justify-center">
                            <LoadingSpinner size="lg" />
                            <p className="mt-6 text-gray-500 font-mono text-xs animate-pulse uppercase tracking-[0.2em]">Synthesizing Intelligence...</p>
                        </div>
                    )}

                    {analysisResults && (
                        <div className="grid grid-cols-1 gap-6 pb-20">
                            {analysisResults.map((result, idx) => (
                                <div
                                    key={result.trace_id || idx}
                                    onClick={() => navigate(`/groups/${result.trace_id}`)}
                                    className="bg-black/40 backdrop-blur border border-white/10 rounded-2xl p-6 hover:border-electric-blue/50 hover:bg-white/5 transition-all group relative overflow-hidden cursor-pointer"
                                >
                                    <div className="absolute top-0 right-0 p-4 opacity-10 font-black text-6xl select-none group-hover:opacity-20 transition-opacity">
                                        {idx + 1}
                                    </div>

                                    <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider
                                                    ${result.priority?.includes('P0') ? 'bg-alert-red/20 text-alert-red' : 'bg-gray-700 text-gray-300'}
                                                `}>
                                                    {result.priority || 'P2'}
                                                </span>
                                                <span className="text-gray-500 font-mono text-[10px]">TRACE: {result.trace_id?.slice(0, 12)}...</span>
                                            </div>
                                            <h4 className="text-lg font-bold text-gray-100 group-hover:text-electric-blue transition-colors">
                                                {result.root_cause || "Unidentified Anomaly"}
                                            </h4>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-[10px] font-bold text-gray-500 uppercase">Confidence</div>
                                            <div className="text-xl font-mono text-electric-blue">
                                                {result.confidence}%
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                                        <div className="space-y-3">
                                            <div>
                                                <h5 className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-1">Correlation Insight</h5>
                                                <p className="text-sm text-gray-400 leading-relaxed italic">"{result.correlation || "No correlation data available."}"</p>
                                            </div>
                                            <div>
                                                <h5 className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-1">Recommended Action</h5>
                                                <div className="bg-success-green/5 border border-success-green/20 rounded-lg p-3 text-sm text-success-green">
                                                    {result.action}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                                            <h5 className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-2">Redacted Trace Summary</h5>
                                            <p className="text-xs text-gray-500 font-mono leading-relaxed overflow-hidden line-clamp-6">
                                                {result.redacted_text}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Reuse Deep Dive Panel */}
            <DeepDivePanel
                isOpen={!!selectedGroup}
                onClose={() => setSelectedGroup(null)}
                group={selectedGroup}
            />
        </div>
    );
};

export default DashboardPage;
