import React, { useState } from 'react';
import IncidentTimeline from '../visuals/IncidentTimeline';
import SecureLogViewer from '../visuals/SecureLogViewer';

const InvestigationCanvas = ({ group, incidents }) => {
    const [selectedTab, setSelectedTab] = useState('reasoning');

    return (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[600px]">

            {/* LEFT: Pattern Context (4 cols) */}
            <div className="lg:col-span-4 space-y-6">
                {/* Timeline Card */}
                <div className="bg-white/5 backdrop-blur border border-white/10 rounded-xl p-5 shadow-lg">
                    <h3 className="text-sm font-bold text-gray-300 mb-4 flex items-center gap-2">
                        <svg className="w-4 h-4 text-electric-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Temporal Pattern
                    </h3>
                    <div className="max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                        <IncidentTimeline incidents={incidents} />
                    </div>
                    <p className="text-xs text-gray-500 mt-4 text-center italic">
                        Drag to zoom into specific anomaly windows
                    </p>
                </div>

                {/* Cluster/Batch Info */}
                <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 border border-indigo-500/20 rounded-xl p-5 flex flex-col items-center text-center">
                    <div className="text-4xl font-bold text-white mb-2">{group.count || 1}</div>
                    <div className="text-xs text-indigo-300 uppercase font-mono tracking-widest mb-4">Occurrences Detected</div>
                    <div className="w-full bg-black/20 rounded-lg p-3 text-left">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>First Seen</span>
                            <span className="text-gray-200 font-mono">2h ago</span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-400">
                            <span>Last Seen</span>
                            <span className="text-electric-blue font-mono">Just now</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* RIGHT: Investigation & Evidence (8 cols) */}
            <div className="lg:col-span-8 bg-white/5 backdrop-blur border border-white/10 rounded-xl flex flex-col overflow-hidden shadow-2xl">
                {/* Tabs */}
                <div className="flex border-b border-white/10">
                    <button
                        onClick={() => setSelectedTab('reasoning')}
                        className={`px-6 py-4 text-sm font-bold tracking-wide transition-colors ${selectedTab === 'reasoning' ? 'bg-white/5 text-electric-blue border-b-2 border-electric-blue' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        AI Reasoning Analysis
                    </button>
                    <button
                        onClick={() => setSelectedTab('evidence')}
                        className={`px-6 py-4 text-sm font-bold tracking-wide transition-colors ${selectedTab === 'evidence' ? 'bg-white/5 text-electric-blue border-b-2 border-electric-blue' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        Forensic Evidence (Logs)
                    </button>
                    <button
                        onClick={() => setSelectedTab('playbook')}
                        className={`px-6 py-4 text-sm font-bold tracking-wide transition-colors ${selectedTab === 'playbook' ? 'bg-white/5 text-electric-blue border-b-2 border-electric-blue' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        Remediation Playbook
                    </button>
                </div>

                {/* Content Area */}
                <div className="p-6 flex-1 overflow-y-auto max-h-[600px] custom-scrollbar">

                    {selectedTab === 'reasoning' && (
                        <div className="space-y-8 animate-fade-in">
                            {/* Gemini Analysis Steps */}
                            <div className="flex items-start gap-4">
                                <div className="w-8 h-8 rounded-full bg-electric-blue/20 flex items-center justify-center text-electric-blue font-bold text-sm border border-electric-blue/30 shrink-0">1</div>
                                <div>
                                    <h4 className="text-gray-200 font-bold text-lg mb-1">Root Cause Analysis</h4>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {group.analysis?.cause || "No automated cause identified."}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start gap-4">
                                <div className="w-8 h-8 rounded-full bg-electric-blue/20 flex items-center justify-center text-electric-blue font-bold text-sm border border-electric-blue/30 shrink-0">2</div>
                                <div>
                                    <h4 className="text-gray-200 font-bold text-lg mb-1">Correlation & Insight</h4>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {group.analysis?.correlation_insight || "No specific correlation insights detected across traces."}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start gap-4">
                                <div className="w-8 h-8 rounded-full bg-electric-blue/20 flex items-center justify-center text-electric-blue font-bold text-sm border border-electric-blue/30 shrink-0">3</div>
                                <div>
                                    <h4 className="text-gray-200 font-bold text-lg mb-1">AI Hypothesis</h4>
                                    <div className="bg-black/30 border border-white/5 rounded-lg p-4 mt-2">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-bold text-gray-300">Analysis Summary</span>
                                            <span className="text-xs bg-success-green/20 text-success-green px-2 py-0.5 rounded font-mono">
                                                {((group.root_cause?.confidence || 0) * 100).toFixed(0)}% Confidence
                                            </span>
                                        </div>
                                        <p className="text-gray-400 text-sm">
                                            {group.analysis?.redacted_summary || "Gemini concluded its scan focusing on security and priority parameters."}
                                        </p>
                                    </div>
                                    {group.analysis?.security_alert && (
                                        <div className="bg-alert-red/10 border border-alert-red/20 rounded-lg p-4 mt-2">
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className="text-alert-red">⚠️ SECURITY ALERT DETECTED</span>
                                            </div>
                                            <p className="text-gray-400 text-sm italic underline">
                                                Potential security vulnerability detected in this trace pattern.
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {selectedTab === 'evidence' && (
                        <div className="h-full animate-fade-in">
                            <SecureLogViewer logs={group.logs || []} />
                        </div>
                    )}

                    {selectedTab === 'playbook' && (
                        <div className="space-y-4 animate-fade-in text-gray-300">
                            <h4 className="text-gray-100 font-bold text-lg mb-1">AI Recommended Remedy</h4>
                            <div className="p-5 bg-success-green/5 rounded-xl border border-success-green/20 font-mono text-sm text-success-green leading-relaxed">
                                <div className="flex gap-2 mb-2">
                                    <span className="opacity-50 tracking-tighter">EXECUTE &gt;</span>
                                    <span className="font-bold underline">AUTO-HEAL COMMAND</span>
                                </div>
                                {group.analysis?.action || "No specific playbook actions generated for this anomaly."}
                            </div>
                            <p className="text-[10px] text-gray-500 italic mt-4 uppercase tracking-widest">
                                Source: Gemini SRE Intelligence Layer
                            </p>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default InvestigationCanvas;
