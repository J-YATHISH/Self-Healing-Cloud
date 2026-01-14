import React from 'react';
import { useNavigate } from 'react-router-dom';
import ConfidenceRing from '../visuals/ConfidenceRing';

const IncidentCommandHeader = ({ group }) => {
    const navigate = useNavigate();
    const isActive = group.status === 'OPEN';

    return (
        <div className="fixed top-16 left-64 right-0 z-30 bg-obsidian/95 backdrop-blur-md border-b border-white/10 shadow-2xl transition-all duration-300">
            {/* Top Bar: Nav & High-level Status */}
            <div className="max-w-7xl mx-auto px-6 py-3 flex justify-between items-center">
                <button
                    onClick={() => navigate('/incidents')}
                    className="text-xs font-mono text-gray-500 hover:text-electric-blue transition-colors flex items-center gap-2"
                >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    RETURN TO CANVAS
                </button>
                <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 uppercase tracking-widest font-mono">Incident ID: {group.id}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider border ${isActive
                        ? 'bg-alert-red/10 text-alert-red border-alert-red/20 animate-pulse'
                        : 'bg-success-green/10 text-success-green border-success-green/20'
                        }`}>
                        {isActive ? 'Active Incident' : 'Resolved'}
                    </span>
                </div>
            </div>

            {/* Main Header Content */}
            <div className="max-w-7xl mx-auto px-6 pb-6 pt-2 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

                {/* Title & Signature (Col 1-7) */}
                <div className="lg:col-span-7">
                    <h1 className="text-2xl font-bold text-gray-100 tracking-tight leading-tight mb-2">
                        {group.name}
                    </h1>
                    <div className="text-sm text-gray-400 font-mono bg-black/30 p-2 rounded border border-white/5 inline-block max-w-full truncate">
                        Failure Signature: <span className="text-electric-blue">{group.root_cause?.cause || "Analysis Pending..."}</span>
                    </div>
                </div>

                {/* AI Confidence & Zone Data (Col 8-12) */}
                <div className="lg:col-span-5 flex justify-end items-center border-l border-white/10 pl-6 gap-8">
                    <div className="flex flex-col items-center justify-center">
                        <ConfidenceRing score={group.root_cause?.confidence || 0} size={60} />
                        <span className="text-[10px] text-gray-500 uppercase font-mono mt-2 tracking-wide text-center">AI Certainty</span>
                    </div>
                </div>
            </div>

            {/* Loading / Progress Bar if active */}
            {isActive && (
                <div className="h-0.5 w-full bg-gray-800 overflow-hidden">
                    <div className="h-full bg-electric-blue animate-progress-indeterminate"></div>
                </div>
            )}
        </div>
    );
};

export default IncidentCommandHeader;
