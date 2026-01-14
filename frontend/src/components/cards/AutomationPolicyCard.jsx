import React from 'react';
import ImpactBadge from '../visuals/ImpactBadge';

const AutomationPolicyCard = ({ rule, onEdit, onToggle, onTest, onDelete }) => {
    // Generate derived policy attributes mock
    const scope = rule.severity === 'CRITICAL' ? 'Global' : (rule.severity === 'HIGH' ? 'Infrastructure' : 'Service');

    const handleDelete = () => {
        if (window.confirm(`Are you sure you want to delete the alert rule "${rule.name}"?`)) {
            onDelete(rule.id);
        }
    };

    return (
        <div className={`bg-white/5 backdrop-blur border rounded-xl p-0 transition-all duration-300 hover:scale-[1.01] group ${rule.enabled
            ? 'border-white/10 hover:border-electric-blue/50'
            : 'border-white/5 opacity-60 grayscale hover:opacity-100 hover:grayscale-0'
            }`}>
            {/* Header: Scope & Status */}
            <div className="px-5 py-3 border-b border-white/5 flex justify-between items-center bg-black/20">
                <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-gray-500">#{String(rule.id || 0).slice(-3).padStart(3, '0')}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-white/5 text-gray-400 border border-white/5">
                        Domain: {rule.category || 'General'}
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${rule.enabled ? 'bg-electric-blue animate-pulse' : 'bg-gray-600'}`}></span>
                    <span className={`text-xs font-bold ${rule.enabled ? 'text-electric-blue' : 'text-gray-500'}`}>
                        {rule.enabled ? 'MONITORING' : 'PAUSED'}
                    </span>
                </div>
            </div>

            {/* Body: Policy Definition */}
            <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Trigger */}
                <div className="col-span-2">
                    <h3 className="text-lg font-bold text-gray-100 mb-2 group-hover:text-electric-blue transition-colors">
                        {rule.name}
                    </h3>
                    <div className="flex items-start gap-2 text-sm text-gray-400 mb-2">
                        <span className="min-w-[70px] uppercase text-xs font-mono text-gray-500 mt-0.5">IF</span>
                        <div className="bg-black/40 px-2 py-1 rounded text-electric-blue font-mono border border-white/5">
                            error_count &gt; {rule.threshold} / {rule.window_minutes}min
                        </div>
                    </div>
                    <div className="flex items-start gap-2 text-sm text-gray-400">
                        <span className="min-w-[70px] uppercase text-xs font-mono text-gray-500 mt-0.5">THEN</span>
                        <div className="space-y-1">
                            <div className="flex items-center gap-2">
                                <svg className="w-4 h-4 text-electric-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z" />
                                </svg>
                                <span>Dispatch Gmail Notification to Registered On-Call</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-500">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                                <span>Log Violation to Audit Trace</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Severity & Scope */}
                <div className="border-l border-white/5 pl-6 flex flex-col justify-center">
                    <p className="text-xs uppercase font-mono text-gray-500 mb-2">Priority Level</p>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Severity</span>
                            <span className={`font-mono font-bold ${rule.severity === 'CRITICAL' ? 'text-alert-red' :
                                (rule.severity === 'HIGH' ? 'text-orange-400' : 'text-success-green')
                                }`}>{rule.severity}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Impact Scope</span>
                            <span className="text-white font-mono">{scope}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer: Actions */}
            <div className="bg-white/[0.02] px-5 py-3 border-t border-white/5 flex justify-end gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                    onClick={handleDelete}
                    className="text-xs text-gray-500 hover:text-alert-red flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-alert-red/10 transition-colors"
                >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Delete
                </button>
                <div className="h-4 w-px bg-white/10 my-auto"></div>
                <button
                    onClick={() => onTest(rule)}
                    className="text-xs text-gray-400 hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-white/5 transition-colors"
                >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Test Rule
                </button>
                <div className="h-4 w-px bg-white/10 my-auto"></div>
                <button
                    onClick={() => onToggle(rule)}
                    className="text-xs text-gray-400 hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-white/5 transition-colors"
                >
                    {rule.enabled ? 'Pause Rule' : 'Resume Rule'}
                </button>
                <div className="h-4 w-px bg-white/10 my-auto"></div>
                <button
                    onClick={() => onEdit(rule)}
                    className="text-xs text-electric-blue hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded bg-electric-blue/10 hover:bg-electric-blue/20 border border-electric-blue/20 transition-colors"
                >
                    Edit Config
                </button>
            </div>
        </div>
    );
};

export default AutomationPolicyCard;
