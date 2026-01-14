import React from 'react';

const ConfidenceRing = ({ score = 0, size = 60, strokeWidth = 4 }) => {
    // Normalize score: if it's 0-1 (like 0.98), convert to 0-100
    const normalizedScore = (score > 0 && score <= 1) ? Math.round(score * 100) : Math.round(score);

    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (normalizedScore / 100) * circumference;

    let color = 'text-alert-red';
    if (score >= 80) color = 'text-success-green';
    else if (score >= 50) color = 'text-electric-blue';

    return (
        <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
            {/* Background Ring */}
            <svg className="transform -rotate-90 w-full h-full">
                <circle
                    className="text-gray-800"
                    strokeWidth={strokeWidth}
                    stroke="currentColor"
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                />
                {/* Progress Ring */}
                <circle
                    className={`${color} transition-all duration-1000 ease-out`}
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                />
            </svg>
            {/* Score Text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-sm font-bold ${color}`}>{normalizedScore}%</span>
                <span className="text-[8px] text-gray-500 uppercase tracking-tighter">CONF</span>
            </div>
        </div>
    );
};

export default ConfidenceRing;
