import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import TrendsLineChart from '../components/charts/TrendsLineChart';
import RiskMatrixScatterChart from '../components/charts/RiskMatrixScatterChart';
import StatusPieChart from '../components/charts/StatusPieChart';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AnalysisCapsule from '../components/analytics/AnalysisCapsule';

const AnalyticsPage = () => {
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('7d');
    const [data, setData] = useState({
        trends: [],
        topCategories: [],
        statusDistribution: [],
        riskMatrix: []
    });

    useEffect(() => {
        const fetchAnalytics = async () => {
            setLoading(true);
            try {
                const response = await analyticsAPI.trends({ range: timeRange });
                setData(response.data);
            } catch (err) {
                console.error("Failed to load real analytics:", err);
                // Set empty but valid structure to avoid crashes
                setData({
                    trends: [],
                    topCategories: [],
                    statusDistribution: [],
                    riskMatrix: []
                });
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, [timeRange]);

    if (loading) return <LoadingSpinner size="lg" className="min-h-[50vh]" />;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-end justify-between border-b border-white/10 pb-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-100 tracking-tight">System Intelligence</h1>
                    <p className="mt-1 text-sm text-gray-400 font-mono">Observe behavior, detect anomalies, optimize reliability.</p>
                </div>

                <div className="bg-black/20 border border-white/10 rounded-lg p-1 flex">
                    {['24h', '7d', '30d'].map((range) => (
                        <button
                            key={range}
                            onClick={() => setTimeRange(range)}
                            className={`px-3 py-1 text-xs font-bold rounded transition-colors ${timeRange === range
                                ? 'bg-electric-blue text-black shadow-[0_0_10px_rgba(0,209,255,0.3)]'
                                : 'text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            {range.toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Primary Chart */}
            <div className="h-[400px]">
                <AnalysisCapsule
                    title="Failure Density vs Recovery Response"
                    subtitle="Are we healing faster than we are failing?"
                    insight={data.trends.length > 0 ? "Analyzing current failure density patterns across selected time range." : "No significant traces detected in the current lookback window."}
                >
                    <TrendsLineChart data={data.trends} />
                </AnalysisCapsule>
            </div>

            {/* Secondary Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[350px]">
                <AnalysisCapsule
                    title="Neural Risk Distribution"
                    subtitle="AI CONFIDENCE VS INCIDENT IMPACT MATRIX"
                    insight="High-consequence anomalies with high AI confidence are prioritized in the upper-right quadrant."
                >
                    <RiskMatrixScatterChart data={data.riskMatrix || []} />
                </AnalysisCapsule>

                <AnalysisCapsule
                    title="Resolution Efficiency"
                    subtitle="Current state of incident lifecycle"
                    insight="Real-time distribution of open vs resolved anomalies."
                >
                    <StatusPieChart data={data.statusDistribution} />
                </AnalysisCapsule>
            </div>
        </div>
    );
};

export default AnalyticsPage;
