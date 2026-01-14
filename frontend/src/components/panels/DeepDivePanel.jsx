import React from 'react';
import IncidentSparkline from '../visuals/IncidentSparkline';
import SecureLogViewer from '../visuals/SecureLogViewer';

const DeepDivePanel = ({ isOpen, onClose, group }) => {
    if (!group) return null;

    return (
        <div className={`fixed inset-y-0 right-0 w-full md:w-[600px] bg-obsidian border-l border-white/10 shadow-2xl transform transition-transform duration-300 z-50 ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
            <div className="h-full flex flex-col">
                {/* Header */}
                <div className="h-16 flex items-center justify-between px-6 border-b border-white/10 bg-black/20">
                    <div>
                        <h2 className="text-lg font-bold text-gray-100">Deep Dive Analysis</h2>
                        <span className="text-xs font-mono text-electric-blue">{group.id}</span>
                    </div>
                    <button onClick={onClose} className="text-gray-500 hover:text-white p-2">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8">

                    {/* Section 1: AI Reasoning */}
                    <section>
                        <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-electric-blue"></span>
                            Gemini Reasoning
                        </h3>
                        <div className="bg-white/5 border border-white/5 rounded-lg p-4 space-y-3">
                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-white/10 text-white flex items-center justify-center text-xs font-bold">1</div>
                                <p className="text-sm text-gray-300">Analyzed <strong>{group.count || 50}+</strong> error logs matching signature.</p>
                            </div>
                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-white/10 text-white flex items-center justify-center text-xs font-bold">2</div>
                                <p className="text-sm text-gray-300">Identified root cause as <span className="text-alert-red">Database Connection Timeout</span> correlated with deployment `v1.2.4`.</p>
                            </div>
                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-white/10 text-white flex items-center justify-center text-xs font-bold">3</div>
                                <p className="text-sm text-gray-300">Confidence is high ({group.root_cause?.confidence}%) due to exact stack trace match with previous incidents.</p>
                            </div>
                        </div>
                    </section>

                    {/* Section 2: Timeline */}
                    <section>
                        <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-electric-blue"></span>
                            Temporal Analysis
                        </h3>
                        <div className="bg-white/5 border border-white/5 rounded-lg p-4">
                            <IncidentSparkline />
                            <div className="flex justify-between text-[10px] text-gray-600 font-mono mt-2">
                                <span>-24h</span>
                                <span>NOW</span>
                            </div>
                        </div>
                    </section>

                    {/* Section 3: Secure Logs */}
                    <section>
                        <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-electric-blue"></span>
                            Evidence Locker
                        </h3>
                        <SecureLogViewer />
                    </section>

                </div>

                {/* Footer Actions */}
                <div className="border-t border-white/10 p-4 bg-black/20 flex justify-end gap-3">
                    <button onClick={onClose} className="px-4 py-2 rounded text-gray-400 hover:text-white text-sm">Close</button>
                    <button className="px-4 py-2 bg-electric-blue text-black font-bold rounded shadow-[0_0_15px_rgba(0,209,255,0.3)] hover:bg-electric-blue/90 text-sm">
                        View Full Trace
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DeepDivePanel;
