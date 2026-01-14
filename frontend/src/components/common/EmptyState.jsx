import React from 'react';

const EmptyState = ({
    title = "No data available",
    description = "There is nothing to display here yet.",
    icon = null,
    action = null
}) => {
    return (
        <div className="flex flex-col items-center justify-center p-12 text-center bg-slate-900/50 backdrop-blur-md rounded-2xl border border-slate-800 shadow-2xl min-h-[400px] transition-all animate-fade-in">
            <div className="bg-electric-blue/5 p-5 rounded-full mb-6 ring-1 ring-electric-blue/20">
                {icon || (
                    <svg className="w-10 h-10 text-electric-blue drop-shadow-[0_0_8px_rgba(0,209,255,0.4)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                )}
            </div>
            <h3 className="text-xl font-bold text-gray-100 mb-2 tracking-tight">{title}</h3>
            <p className="text-gray-400 max-w-md mb-8 leading-relaxed font-mono text-sm">{description}</p>
            {action && (
                <div className="animate-pulse-slow">
                    {action}
                </div>
            )}
        </div>
    );
};

export default EmptyState;
