import React from 'react';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ZAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';

const RiskMatrixScatterChart = ({ data }) => {
    const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#6366f1'];

    // Custom tooltip for SRE context
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const item = payload[0].payload;
            return (
                <div className="bg-[#0B0E14] border border-white/10 p-3 rounded-lg shadow-xl backdrop-blur-md">
                    <p className="text-gray-400 text-[10px] font-mono mb-1 uppercase tracking-widest">Incident: {item.id}</p>
                    <p className="text-white font-bold text-sm mb-2">{item.label}</p>
                    <div className="space-y-1">
                        <div className="flex justify-between gap-4 text-xs font-mono">
                            <span className="text-gray-500">Service:</span>
                            <span className="text-electric-blue">{item.service}</span>
                        </div>
                        <div className="flex justify-between gap-4 text-xs font-mono">
                            <span className="text-gray-500">Confidence:</span>
                            <span className="text-success-green">{item.confidence}%</span>
                        </div>
                        <div className="flex justify-between gap-4 text-xs font-mono">
                            <span className="text-gray-500">Log Intensity:</span>
                            <span className="text-alert-red">{item.impact}</span>
                        </div>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="h-full w-full">
            <ResponsiveContainer width="100%" height="100%">
                <ScatterChart
                    margin={{
                        top: 20,
                        right: 20,
                        bottom: 20,
                        left: 20,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} vertical={false} />
                    <XAxis
                        type="number"
                        dataKey="confidence"
                        name="Confidence"
                        unit="%"
                        stroke="#4b5563"
                        fontSize={10}
                        domain={[0, 100]}
                        label={{ value: 'Confidence', position: 'insideBottom', offset: -10, fontSize: 10, fill: '#6b7280' }}
                    />
                    <YAxis
                        type="number"
                        dataKey="impact"
                        name="Impact"
                        stroke="#4b5563"
                        fontSize={10}
                        label={{ value: 'Log Impact', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#6b7280' }}
                    />
                    <ZAxis type="number" range={[100, 400]} />
                    <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter name="Anomalies" data={data} fill="#6366f1">
                        {data.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.confidence > 80 ? '#10b981' : entry.confidence > 50 ? '#3b82f6' : '#ef4444'}
                                fillOpacity={0.6}
                                stroke={entry.confidence > 80 ? '#10b981' : entry.confidence > 50 ? '#3b82f6' : '#ef4444'}
                                strokeWidth={2}
                            />
                        ))}
                    </Scatter>
                </ScatterChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RiskMatrixScatterChart;
