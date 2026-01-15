import React from 'react';
import { Link } from 'react-router-dom';

const IncidentTimeline = ({ incidents = [] }) => {
    if (!incidents.length) {
        return <div className="text-sm text-gray-500 italic p-4">No recent incidents found.</div>;
    }

    return (
        <div className="flow-root">
            <ul className="-mb-8">
                {incidents.map((incident, incidentIdx) => (
                    <li key={incident.id}>
                        <div className="relative pb-8">
                            {incidentIdx !== incidents.length - 1 ? (
                                <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-700" aria-hidden="true" />
                            ) : null}
                            <div className="relative flex space-x-3">
                                <div>
                                    <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-gray-900 ${incident.status === 'RESOLVED' ? 'bg-green-500' :
                                        incident.status === 'INVESTIGATING' ? 'bg-purple-500' : 'bg-red-500'
                                        }`}>
                                        <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            {incident.status === 'RESOLVED' ? (
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            ) : (
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01" />
                                            )}
                                        </svg>
                                    </span>
                                </div>
                                <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                                    <div>
                                        <p className="text-sm text-gray-400">
                                            Anomaly in <span className="font-medium text-gray-100">{incident.service_name || 'System'}</span>
                                            <span className="text-[10px] text-gray-600 ml-2 font-mono">{incident.trace_id?.slice(0, 8)}</span>
                                        </p>
                                    </div>
                                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                                        <time dateTime={incident.timestamp}>{new Date(incident.timestamp).toLocaleString()}</time>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default IncidentTimeline;
