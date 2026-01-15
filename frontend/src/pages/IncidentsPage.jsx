import React, { useState, useEffect } from 'react';
import { groupsAPI } from '../services/api';
import { ERROR_CATEGORIES } from '../constants/errorCategories';
import IncidentCanvasCard from '../components/cards/IncidentCanvasCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';

import DeepDivePanel from '../components/panels/DeepDivePanel';

const IncidentsPage = () => {
    // State
    const [groups, setGroups] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [selectedGroup, setSelectedGroup] = useState(null); // For Deep Dive Panel
    const [filters, setFilters] = useState({
        search: '',
        severity: 'ALL',
        status: 'ALL',
        category: 'ALL'
    });

    // Mock Pagination Config
    const PAGE_SIZE = 10;
    const [hasMore, setHasMore] = useState(true);

    // Fetch Error Groups (Canvas Items)
    useEffect(() => {
        const fetchGroups = async () => {
            setLoading(true);
            try {
                // Prepare params
                const params = {
                    page: page,
                    limit: PAGE_SIZE,
                    ...(filters.search && { search: filters.search }),
                    ...(filters.severity !== 'ALL' && { severity: filters.severity }),
                    ...(filters.status !== 'ALL' && { status: filters.status }),
                    ...(filters.category !== 'ALL' && { category: filters.category }),
                };

                const response = await groupsAPI.list(params);
                setGroups(response.data);

                // Simple hasMore logic
                setHasMore(response.data.length === PAGE_SIZE);

            } catch (err) {
                console.error("Failed to load error groups", err);
                setGroups([]);
            } finally {
                setLoading(false);
            }
        };

        const debounceFetch = setTimeout(() => {
            fetchGroups();
        }, 500);

        return () => clearTimeout(debounceFetch);
    }, [page, filters]);

    // Handlers
    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
        setPage(1);
    };

    return (
        <div className="space-y-6">
            <div className="sm:flex sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-100">Incident Canvas</h1>
                    <p className="mt-1 text-sm text-gray-400">Batch-oriented analysis of active error patterns.</p>
                </div>
                {/* Stats or Global Actions could go here */}
            </div>

            {/* Filters */}
            <div className="bg-white/5 border border-white/10 p-4 rounded-xl shadow-lg backdrop-blur grid grid-cols-1 sm:grid-cols-5 gap-4">
                <div className="sm:col-span-2">
                    <label htmlFor="search" className="sr-only">Search</label>
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                        <input
                            type="text"
                            name="search"
                            id="search"
                            className="bg-black/20 block w-full pl-10 sm:text-sm border-white/10 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-electric-blue focus:border-electric-blue py-2.5"
                            placeholder="Search by error pattern or service..."
                            value={filters.search}
                            onChange={handleFilterChange}
                        />
                    </div>
                </div>

                <div>
                    <select
                        name="severity"
                        value={filters.severity}
                        onChange={handleFilterChange}
                        className="bg-black/20 block w-full pl-3 pr-10 py-2.5 text-base border-white/10 text-gray-200 focus:outline-none focus:ring-electric-blue focus:border-electric-blue sm:text-sm rounded-lg"
                    >
                        <option value="ALL">Severity: All</option>
                        <option value="CRITICAL">Critical Only</option>
                        <option value="HIGH">High Priority</option>
                    </select>
                </div>
                <div>
                    <select
                        name="status"
                        value={filters.status}
                        onChange={handleFilterChange}
                        className="bg-black/20 block w-full pl-3 pr-10 py-2.5 text-base border-white/10 text-gray-200 focus:outline-none focus:ring-electric-blue focus:border-electric-blue sm:text-sm rounded-lg"
                    >
                        <option value="ALL">Status: All</option>
                        <option value="OPEN">Open Issues</option>
                        <option value="RESOLVED">Resolved</option>
                    </select>
                </div>

                <div>
                    <select
                        name="category"
                        value={filters.category}
                        onChange={handleFilterChange}
                        className="bg-black/20 block w-full pl-3 pr-10 py-2.5 text-base border-white/10 text-gray-200 focus:outline-none focus:ring-electric-blue focus:border-electric-blue sm:text-sm rounded-lg"
                    >
                        <option value="ALL">Category: All</option>
                        {ERROR_CATEGORIES.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Canvas Header */}
            <div className="flex items-center justify-between text-xs text-gray-500 uppercase tracking-wider font-semibold px-2">
                <span>Active Batches ({groups.length})</span>
                <span>AI Confidence & Actions</span>
            </div>

            {/* Content Canvas */}
            {
                loading ? (
                    <div className="flex items-center justify-center min-h-[400px]">
                        <LoadingSpinner size="lg" />
                    </div>
                ) : groups.length === 0 ? (
                    <EmptyState
                        title="No active batches found"
                        description="Your system is running smoothly. No error patterns detected fitting current filters."
                    />
                ) : (
                    <div className="grid grid-cols-1 gap-4">
                        {groups.map(group => (
                            <IncidentCanvasCard key={group.id} group={group} />
                        ))}
                    </div>
                )
            }

            {/* Pagination / Load More */}
            <div className="flex justify-center mt-8">
                <div className="inline-flex rounded-md shadow-sm bg-white/5 border border-white/10">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-white/5 rounded-l-md disabled:opacity-50"
                    >
                        Previous
                    </button>
                    <div className="px-4 py-2 text-sm text-gray-500 border-l border-r border-white/10">
                        Page {page}
                    </div>
                    <button
                        onClick={() => setPage(p => p + 1)}
                        disabled={!hasMore}
                        className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-white/5 rounded-r-md disabled:opacity-50"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    );
};

export default IncidentsPage;
