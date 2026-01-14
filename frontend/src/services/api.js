import axios from 'axios';

// Create Axios instance
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for API calls
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Server responded with error status
            const status = error.response.status;
            if (status === 503) {
                console.error('Backend service unavailable. Please ensure the backend is running.');
            } else if (status === 404) {
                console.error('Resource not found:', error.config.url);
            } else if (status === 500) {
                console.error('Server error:', error.response.data?.detail || 'Internal server error');
            }
        } else if (error.request) {
            // Request made but no response
            console.error('No response from backend. Is the server running on http://localhost:8000?');
        } else {
            console.error('Request error:', error.message);
        }
        return Promise.reject(error);
    }
);

// Auth API Services
export const authAPI = {
    googleAuthorize: (projectId) => api.get('/auth/google/authorize', { params: { project_id: projectId } }),
    googleStatus: () => api.get('/auth/google/status'),
    setup: (config) => api.post('/auth/setup', config),
    login: (credentials) => api.post('/auth/login', credentials),
    status: () => api.get('/auth/status'),
};

// Analysis API Services
export const analysisAPI = {
    start: (params) => api.post('/analyze/start', params),
    status: (task_id) => api.get(`/analyze/status/${task_id}`),
};

// Incidents API Services
export const incidentsAPI = {
    list: (params) => api.get('/incidents', { params }),
    detail: (id) => api.get(`/incidents/${id}`),
};

// Groups API Services
export const groupsAPI = {
    list: (params) => api.get('/groups', { params }), // Allow passing query params like { status: 'active' }
    detail: (id) => api.get(`/groups/${id}`),
    playbook: (id) => api.get(`/groups/${id}/playbook`),
};

// Analytics API Services
export const analyticsAPI = {
    summary: () => api.get('/analytics/summary'),
    trends: (params) => api.get('/analytics/trends', { params }),
};

// Alerts API Services
export const alertsAPI = {
    list: () => api.get('/alerts/rules'),
    create: (rule) => api.post('/alerts/rules', rule),
    update: (id, rule) => api.put(`/alerts/rules/${id}`, rule),
    delete: (id) => api.delete(`/alerts/rules/${id}`),
};

// Security API Services
export const securityAPI = {
    redactions: () => api.get('/security/redactions'),
};

// Chat API Services
export const chatAPI = {
    send: (message) => api.post('/chat', { message }),
};

export default api;
