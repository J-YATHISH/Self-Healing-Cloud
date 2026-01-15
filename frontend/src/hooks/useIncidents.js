import { useState, useCallback } from 'react';
import { incidentsAPI } from '../services/api';

export const useIncidents = () => {
    const [incidents, setIncidents] = useState([]);
    const [incident, setIncident] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchIncidents = useCallback(async (params = {}) => {
        setLoading(true);
        setError(null);
        try {
            // Backend filtering: GET /api/incidents?category=<CATEGORY>
            const response = await incidentsAPI.list(params);
            setIncidents(response.data);
            return response.data;
        } catch (err) {
            setError(err.message || 'Failed to fetch incidents');
            console.error(err);
            if (import.meta.env.DEV) {
                // Mock fallback
                const mock = Array(5).fill(null).map((_, i) => ({
                    id: `INC-${Date.now()}-${i}`,
                    name: `Mock Incident ${i}`,
                    severity: 'HIGH',
                    status: 'OPEN',
                    created_at: new Date().toISOString()
                }));
                setIncidents(mock);
                return mock;
            }
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchIncidentById = useCallback(async (id) => {
        setLoading(true);
        setError(null);
        try {
            const response = await incidentsAPI.detail(id);
            setIncident(response.data);
            return response.data;
        } catch (err) {
            setError(err.message || 'Failed to fetch incident details');
            console.error(err);
            if (import.meta.env.DEV) {
                const mock = {
                    id,
                    name: "Mock Incident Detail",
                    severity: 'CRITICAL',
                    status: 'INVESTIGATING',
                    created_at: new Date().toISOString(),
                    timeline: []
                };
                setIncident(mock);
                return mock;
            }
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        incidents,
        incident,
        loading,
        error,
        fetchIncidents,
        fetchIncidentById
    };
};
