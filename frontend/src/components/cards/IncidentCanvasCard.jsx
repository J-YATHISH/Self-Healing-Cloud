import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ConfidenceRing from '../visuals/ConfidenceRing';

const IncidentCanvasCard = ({ group }) => {
    const [expanded, setExpanded] = useState(false);

    // Safe fallbacks
    const {
        id,
        name,
        count = 1,
        root_cause = {},
        status = 'OPEN',
        last_seen,
        services = ['Unknown Service'],
        route = '/api/unknown'
    } = group;

    const confidence = root_cause.confidence ? (root_cause.confidence <= 1 ? Math.round(root_cause.confidence * 100) : Math.round(root_cause.confidence)) : 0;
    const canRollback = confidence >= 70;

    return (
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-5 mb-4 hover:border-electric-blue/30 transition-all duration-300 group relative overflow-hidden">
            {/* Glow Effect */}
            <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-electric-blue to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

            <div className="flex justify-between items-start gap-4">
                {/* Left: Info & Context */}
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="bg-electric-blue/10 text-electric-blue text-xs font-mono px-2 py-0.5 rounded border border-electric-blue/20">
                            {services[0]}
                        </span>
                        <span className="text-gray-500 text-xs font-mono">{route}</span>
                        <span className="text-gray-600 text-xs">• {new Date(last_seen).toLocaleTimeString()}</span>
                    </div>

                    <Link to={`/groups/${id}`} className="block">
                        <h3 className="text-lg font-semibold text-gray-100 mb-2 group-hover:text-electric-blue transition-colors">
                            {name}
                        </h3>
                    </Link>

                    <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                        {root_cause.cause || "Analysis pending..."}
                    </p>

                    <div className="flex items-center gap-3 mt-4">
                        <div className="flex items-center gap-1 text-xs text-gray-500 bg-black/20 px-2 py-1 rounded" title="Grouped by pattern similarity">
                            <svg className="w-3 h-3 text-electric-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                            <span>x{count} Occurrences</span>
                        </div>
                    </div>
                </div>

                {/* Right: AI & Confidence */}
                <div className="flex flex-col items-end gap-4 min-w-[120px]">
                    <ConfidenceRing score={confidence} size={56} />

                    <div className="flex flex-col gap-2 w-full">
                        <Link
                            to={`/groups/${id}`}
                            className="bg-white/5 hover:bg-white/10 text-gray-300 text-xs py-1.5 px-3 rounded text-center border border-white/5 transition-colors"
                        >
                            View Reasoning
                        </Link>

                        <button
                            disabled={!canRollback}
                            className={`text-xs py-1.5 px-3 rounded text-center font-medium border transition-all
                                ${canRollback
                                    ? 'bg-electric-blue/10 text-electric-blue border-electric-blue/20 hover:bg-electric-blue/20 cursor-pointer'
                                    : 'bg-transparent text-gray-600 border-gray-800 cursor-not-allowed opacity-50'
                                }
                            `}
                            title={canRollback ? "Auto-revert caused by recent deployment" : "Confidence too low for auto-action"}
                        >
                            Approve Rollback
                        </button>
                    </div>
                </div>
            </div>

            {/* Expandable Log Preview */}
            <div className="mt-4 border-t border-white/5 pt-3">
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
                >
                    <svg className={`w-3 h-3 transform transition-transform ${expanded ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    {expanded ? 'Hide Sample Logs' : 'View Redacted Sample Logs'}
                </button>

                {expanded && (
                    <div className="mt-2 bg-black/40 rounded p-3 font-mono text-xs text-gray-400 overflow-x-auto border border-white/5 space-y-2">
                        {(group.logs || []).slice(0, 3).map((log, lidx) => (
                            <div key={lidx} className="border-b border-white/5 pb-2 last:border-0">
                                <div className="flex gap-2 mb-1">
                                    <span className={log.severity === 'ERROR' ? 'text-alert-red' : 'text-gray-500'}>
                                        [{log.severity || 'INFO'}]
                                    </span>
                                    <span className="text-gray-300">{log.message || log.msg}</span>
                                </div>
                                <div className="pl-4 text-[10px] text-gray-600 italic">
                                    {log.timestamp} • {log.service}
                                </div>
                            </div>
                        ))}
                        {(!group.logs || group.logs.length === 0) && (
                            <div className="text-gray-600 italic">No sample logs available for this trace.</div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default IncidentCanvasCard;
