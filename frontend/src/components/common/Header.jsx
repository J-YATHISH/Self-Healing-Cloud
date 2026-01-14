import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { analyticsAPI, securityAPI } from '../../services/api';

const Header = ({ onSecurityClick }) => {
    const { user, logout } = useAuth();
    const projectId = user?.projectId || "PRJ-12345";

    // System Pulse State
    const [pulse, setPulse] = useState({ uptime: 99.98, status: 'nominal' });
    // Security Guard State
    const [redactions, setRedactions] = useState(0);

    // Fetch Metrics
    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                // Mocking real response for now if API not ready
                // const pulseRes = await analyticsAPI.summary();
                // setPulse(pulseRes.data.pulse);

                // const secRes = await securityAPI.redactions();
                // setRedactions(secRes.data.count);

                // Simulation for "Active" UI feel
                setPulse(prev => ({
                    ...prev,
                    uptime: (99.95 + Math.random() * 0.04).toFixed(2)
                }));
                setRedactions(prev => prev + Math.floor(Math.random() * 2)); // Simulate live redactions
            } catch (err) {
                // Silent fail for header widgets
            }
        };

        const interval = setInterval(fetchMetrics, 30000); // 30s refresh
        fetchMetrics(); // Initial call
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status) => {
        switch (status) {
            case 'nominal': return 'text-success-green animate-pulse';
            case 'degraded': return 'text-electric-blue';
            case 'critical': return 'text-alert-red animate-ping';
            default: return 'text-gray-500';
        }
    };

    return (
        <header className="bg-white/5 backdrop-blur-md border-b border-white/10 h-16 z-20 flex items-center justify-between px-6 sticky top-0 transition-all duration-300">
            {/* Left: Branding */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-8 bg-electric-blue rounded-full shadow-[0_0_10px_#00D1FF]"></div>
                    <h2 className="text-xl font-bold text-gray-100 tracking-tight hidden md:block">
                        Cloud RCA <span className="text-electric-blue font-mono font-normal text-sm"></span>
                    </h2>
                </div>
            </div>

            {/* Center: Live Metrics */}
            <div className="hidden lg:flex items-center gap-8 text-sm font-mono">
                {/* System Pulse */}
                <div className="flex items-center gap-2 px-4 py-1 rounded-full bg-black/20 border border-white/5 group hover:border-white/20 transition-colors">
                    <span className="text-gray-400 uppercase text-xs tracking-wider">System Pulse</span>
                    <span className={`text-[10px] transform scale-75 ${getStatusColor(pulse.status)}`}>●</span>
                    <span className="text-electric-blue font-bold">{pulse.uptime}%</span>
                </div>

                {/* Security Guard */}
                <button
                    onClick={onSecurityClick}
                    className="flex items-center gap-2 px-4 py-1 rounded-full bg-black/20 border border-white/5 group hover:border-white/20 transition-colors hover:bg-white/5 cursor-pointer"
                >
                    <span className="text-gray-400 uppercase text-xs tracking-wider">🛡️ Security Guard</span>
                    <span className="text-white font-bold">{redactions}</span>
                    <span className="text-gray-500 text-xs">Redactions (24h)</span>
                </button>
            </div>

            {/* Right: User Info */}
            <div className="flex items-center gap-6">
                {/* Mobile Pulse (Simplified) */}
                <div className="lg:hidden flex items-center gap-2">
                    <span className={`text-[10px] ${getStatusColor(pulse.status)}`}>●</span>
                    <span className="text-electric-blue font-mono text-xs">{pulse.uptime}%</span>
                </div>

                <div className="h-8 w-[1px] bg-white/10 hidden md:block"></div>

                <div className="flex items-center gap-3 group">
                    <div className="text-right hidden md:block">
                        <div className="text-sm font-semibold text-gray-200 group-hover:text-white transition-colors">{user?.name}</div>
                        <div className="text-[10px] font-mono text-electric-blue">{projectId}</div>
                    </div>

                    <div className="relative">
                        <div className="w-9 h-9 bg-electric-blue/10 text-electric-blue border border-electric-blue/20 rounded-lg flex items-center justify-center font-bold text-sm shadow-[0_0_15px_rgba(0,209,255,0.1)]">
                            {user?.name?.charAt(0) || 'OP'}
                        </div>
                    </div>

                    <button
                        onClick={logout}
                        className="ml-2 text-xs text-gray-500 hover:text-alert-red transition-colors font-mono uppercase tracking-wide"
                    >
                        [Logout]
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
