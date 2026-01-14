import React, { useState } from 'react';

const ActionControlPanel = ({ onAction }) => {
    const [executingState, setExecutingState] = useState(null); // 'rollback', 'fix', 'ignore'

    const handleAction = (actionType) => {
        setExecutingState(actionType);
        setTimeout(() => {
            onAction(actionType);
            setExecutingState(null);
        }, 1500);
    };

    return (
        <div className="fixed bottom-0 left-0 right-0 bg-obsidian border-t border-white/10 p-4 pb-6 z-50 shadow-[0_-10px_40px_rgba(0,0,0,0.8)] animate-slide-up">
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">

                <div className="flex items-center gap-4">
                    <div className="text-xs font-mono text-gray-500 uppercase tracking-widest hidden md:block">
                        Human-in-the-Loop Control
                    </div>
                </div>

                <div className="flex items-center gap-4 w-full md:w-auto">
                    {/* Secondary Actions */}
                    <button
                        onClick={() => handleAction('ignore')}
                        disabled={!!executingState}
                        className="flex-1 md:flex-none py-2 px-4 rounded border border-gray-600 text-gray-400 hover:text-white hover:border-gray-400 text-sm font-medium transition-colors disabled:opacity-50"
                    >
                        Mark False Positive
                    </button>

                    <div className="hidden md:flex items-center gap-2 text-[10px] text-gray-600 font-mono italic">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Remediation logic currently manual
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ActionControlPanel;
