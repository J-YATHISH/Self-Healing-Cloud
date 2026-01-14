import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const TrendsLineChart = ({ data, title }) => {
    return (
        <div className="h-full w-full">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart
                    data={data}
                    margin={{
                        top: 10,
                        right: 10,
                        left: -10,
                        bottom: 0,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" opacity={0.3} />
                    <XAxis
                        dataKey="date"
                        stroke="#9ca3af"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                        dy={10}
                    />
                    <YAxis
                        stroke="#9ca3af"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#0B0E14',
                            borderRadius: '8px',
                            border: '1px solid rgba(255,255,255,0.1)',
                            color: '#E5E7EB',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)'
                        }}
                        itemStyle={{ color: '#E5E7EB' }}
                        labelStyle={{ color: '#9CA3AF' }}
                    />
                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                    <Line
                        type="monotone"
                        dataKey="errors"
                        name="Failure Density"
                        stroke="#6366f1"
                        strokeWidth={3}
                        dot={false}
                        activeDot={{ r: 6, fill: '#6366f1', stroke: '#fff' }}
                        animationDuration={1500}
                    />
                    <Line
                        type="monotone"
                        dataKey="anomalies"
                        name="Anomalies"
                        stroke="#ef4444"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={{ r: 4, fill: '#ef4444', strokeWidth: 0 }}
                        animationDuration={2000}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TrendsLineChart;
