import { useState, useCallback } from 'react';
import { groupsAPI } from '../services/api';

export const useErrorGroups = () => {
    const [groups, setGroups] = useState([]);
    const [group, setGroup] = useState(null);
    const [playbook, setPlaybook] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchGroups = useCallback(async (params = {}) => {
        setLoading(true);
        setError(null);
        try {
            // Backend filtering: GET /api/groups?category=<CATEGORY>
            const response = await groupsAPI.list(params);
            setGroups(response.data);
            return response.data;
        } catch (err) {
            setError(err.message || 'Failed to fetch error groups');
            console.error(err);
            if (import.meta.env.DEV) {
                setGroups([
                    { id: 'GRP-1', name: 'Database Timeout', severity: 'CRITICAL', status: 'OPEN', count: 150 },
                    { id: 'GRP-2', name: 'UI Rendering Error', severity: 'MEDIUM', status: 'RESOLVED', count: 45 }
                ]);
            }
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchGroupDetail = useCallback(async (id) => {
        setLoading(true);
        setError(null);
        try {
            const response = await groupsAPI.detail(id);
            setGroup(response.data);
            return response.data;
        } catch (err) {
            setError(err.message || 'Failed to fetch group details');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchPlaybook = useCallback(async (id) => {
        try {
            const response = await groupsAPI.playbook(id);
            setPlaybook(response.data);
            return response.data;
        } catch (err) {
            console.error("Failed to fetch playbook", err);
            if (import.meta.env.DEV) {
                setPlaybook({ steps: ["Restart Service", "Check Logs"] });
            }
        }
    }, []);

    return {
        groups,
        group,
        playbook,
        loading,
        error,
        fetchGroups,
        fetchGroupDetail,
        fetchPlaybook
    };
};
