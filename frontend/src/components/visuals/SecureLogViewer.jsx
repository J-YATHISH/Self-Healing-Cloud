import React, { useState } from 'react';

const SecureLogViewer = ({ logs = [] }) => {
    const [decrypted, setDecrypted] = useState(false);
    const [showMfa, setShowMfa] = useState(false);
    const [mfaCode, setMfaCode] = useState('');

    const handleDecryptRequest = () => {
        setShowMfa(true);
    };

    const handleMfaSubmit = (e) => {
        e.preventDefault();
        // Simulation
        if (mfaCode.length > 0) {
            setShowMfa(false);
            setDecrypted(true);
        }
    };

    // Use logs from props
    const displayLogs = logs;

    return (
        <div className="bg-black/40 rounded-lg border border-white/10 font-mono text-xs overflow-hidden relative">
            <div className="px-3 py-2 bg-black/60 border-b border-white/5 flex justify-between items-center text-gray-500">
                <span>/var/logs/service.log</span>
                <span className="flex items-center gap-1">
                    <span className={`w-2 h-2 rounded-full ${decrypted ? 'bg-alert-red' : 'bg-success-green'}`}></span>
                    {decrypted ? 'UNLOCKED' : 'PROTECTED'}
                </span>
            </div>

            <div className="p-4 space-y-1 relative">
                {displayLogs.length === 0 ? (
                    <div className="text-gray-600 italic">No associated logs found for this trace.</div>
                ) : (
                    displayLogs.map((log, idx) => (
                        <div key={idx} className="flex gap-3">
                            <span className={`w-16 shrink-0 ${log.severity === 'ERROR' || log.severity === 'CRITICAL' ? 'text-alert-red' : (log.severity === 'WARNING' ? 'text-yellow-500' : 'text-gray-500')}`}>
                                [{log.severity || 'INFO'}]
                            </span>
                            <span className="text-gray-300">
                                {log.severity === 'SECRET' && !decrypted ? (
                                    <span className="relative inline-block cursor-help group">
                                        <span className="filter blur-[4px] select-none bg-white/10 px-1 rounded">
                                            REDACTED_SECRET_VALUE
                                        </span>
                                        <span className="absolute -top-1 -right-4 text-electric-blue">
                                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                            </svg>
                                        </span>
                                        {/* Tooltip */}
                                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-900 border border-white/10 p-2 rounded w-48 text-center text-[10px] text-gray-400 z-10">
                                            Redacted by Gemini to prevent secret exposure
                                        </span>
                                    </span>
                                ) : (
                                    log.message || log.msg
                                )}
                            </span>
                        </div>
                    ))
                )}
            </div>

            {/* Decrypt Action - Only show if not decrypted */}
            {!decrypted && (
                <div className="border-t border-white/5 bg-black/20 p-2 flex justify-end">
                    <button
                        onClick={handleDecryptRequest}
                        className="text-electric-blue hover:text-white text-xs flex items-center gap-1 px-3 py-1 rounded hover:bg-white/5 transition-colors"
                    >
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                        </svg>
                        Request Decryption
                    </button>
                </div>
            )}

            {/* MFA Modal Simulation */}
            {showMfa && (
                <div className="absolute inset-0 bg-black/80 backdrop-blur-sm z-20 flex items-center justify-center p-4">
                    <div className="bg-obsidian border border-white/10 p-6 rounded-lg shadow-2xl max-w-sm w-full">
                        <h4 className="text-gray-100 font-bold mb-2">Admin Approval Required</h4>
                        <p className="text-gray-400 mb-4">Enter MFA code to decrypt sensitive logs.</p>

                        <form onSubmit={handleMfaSubmit}>
                            <input
                                type="text"
                                className="w-full bg-black/40 border border-white/20 rounded px-3 py-2 text-white text-center tracking-widest text-lg focus:border-electric-blue outline-none mb-4"
                                placeholder="000 000"
                                value={mfaCode}
                                onChange={(e) => setMfaCode(e.target.value)}
                                autoFocus
                            />
                            <div className="flex justify-end gap-2">
                                <button type="button" onClick={() => setShowMfa(false)} className="px-3 py-1 text-gray-400 hover:text-white">Cancel</button>
                                <button type="submit" className="px-3 py-1 bg-electric-blue/10 text-electric-blue border border-electric-blue/20 rounded hover:bg-electric-blue/20">Verify</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SecureLogViewer;
