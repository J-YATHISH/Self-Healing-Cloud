import React from 'react';

const AnalysisCapsule = ({ title, subtitle, insight, children, type = 'default' }) => {
    // Determine glow color based on insight/type (mock logic for now)
    const glowColor = insight?.toLowerCase().includes('anomaly') ? 'shadow-alert-red/20' :
        insight?.toLowerCase().includes('reduced') ? 'shadow-success-green/20' :
            'shadow-electric-blue/10';

    return (
        <div className={`bg-white/5 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden flex flex-col h-full hover:bg-white/[0.07] transition-all duration-300 shadow-lg ${glowColor} group`}>

            {/* Header: The Question & Context */}
            <div className="px-5 py-4 border-b border-white/5 bg-black/20">
                <h3 className="text-gray-100 font-bold text-lg tracking-tight mb-1 group-hover:text-electric-blue transition-colors">
                    {title}
                </h3>
                {subtitle && (
                    <p className="text-gray-500 text-xs font-mono uppercase tracking-wide">
                        {subtitle}
                    </p>
                )}
            </div>

            {/* Body: The Chart */}
            <div className="flex-1 relative min-h-[200px] w-full">
                {/* Subtle Grid Background */}
                <div className="absolute inset-0 opacity-10 pointer-events-none"
                    style={{ backgroundImage: 'radial-gradient(#4f46e5 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
                </div>
                <div className="absolute inset-4">
                    {children}
                </div>
            </div>

            {/* Footer: AI Insight */}
            {insight && (
                <div className="px-5 py-3 bg-gradient-to-r from-electric-blue/10 to-transparent border-t border-white/5 flex items-start gap-3">
                    <div className="mt-0.5 min-w-[16px]">
                        <svg className="w-4 h-4 text-electric-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div>
                        <span className="text-xs font-bold text-electric-blue uppercase mr-2">AI Insight:</span>
                        <span className="text-xs text-gray-300 italic">"{insight}"</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalysisCapsule;
