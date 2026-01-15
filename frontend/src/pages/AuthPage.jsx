import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const AuthPage = () => {
    const { user, login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    // Redirect if already authenticated
    React.useEffect(() => {
        if (user) {
            navigate('/dashboard', { replace: true });
        }
    }, [user, navigate]);

    // Get redirect location or default to dashboard
    const from = location.state?.from?.pathname || "/dashboard";

    const [step, setStep] = useState(1); // 1: Setup, 2: Login
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const [formData, setFormData] = useState({
        projectId: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear error when user types
        if (error) setError(null);
    };

    const handleSetup = async (e) => {
        e.preventDefault();

        // No validation needed, just proceed to OAuth
        setStep(2);
    };

    const handleLogin = async () => {
        setIsLoading(true);
        setError(null);

        try {
            // Store project_id in sessionStorage for OAuth callback
            sessionStorage.setItem('oauth_project_id', formData.projectId);

            // Get OAuth authorization URL from backend
            const response = await authAPI.googleAuthorize(formData.projectId);
            const { authorization_url } = response.data;

            // Redirect to Google OAuth consent screen
            window.location.href = authorization_url;
        } catch (err) {
            console.error("OAuth initiation failed:", err);
            setError("Failed to connect to Google. Please try again.");
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                    Cloud RCA Assistant
                </h2>
                <p className="mt-2 text-center text-sm text-gray-600">
                    Automated Root Cause Analysis for GCP
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">

                    {error && (
                        <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded text-sm flex items-start">
                            <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <span>{error}</span>
                        </div>
                    )}

                    {step === 1 && (
                        <form className="space-y-6" onSubmit={handleSetup}>
                            <div>
                                <label htmlFor="projectId" className="block text-sm font-medium text-gray-700">
                                    GCP Project ID
                                </label>
                                <div className="mt-1">
                                    <input
                                        id="projectId"
                                        name="projectId"
                                        type="text"
                                        required
                                        placeholder="project-e2bcb697-e160-439a-a3c"
                                        className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                        value={formData.projectId}
                                        onChange={handleChange}
                                    />
                                </div>
                                <p className="mt-2 text-xs text-gray-500">
                                    Recommended: <code className="bg-gray-100 px-1 rounded">project-e2bcb697-e160-439a-a3c</code>
                                </p>
                            </div>

                            <div>
                                <button
                                    type="submit"
                                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    Continue
                                </button>
                            </div>
                        </form>
                    )}

                    {step === 2 && (
                        <div className="space-y-6">
                            <div className="text-center">
                                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
                                    <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <h3 className="text-lg leading-6 font-medium text-gray-900">Ready to Connect</h3>
                                <p className="mt-2 text-sm text-gray-500">
                                    Project <strong>{formData.projectId}</strong> will be linked to your Google account.
                                </p>
                            </div>

                            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                                <div className="flex">
                                    <div className="flex-shrink-0">
                                        <svg className="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    <div className="ml-3 flex-1">
                                        <p className="text-sm text-blue-700">
                                            You'll be redirected to Google to sign in. We'll automatically get your name and email from your Google account.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={handleLogin}
                                disabled={isLoading}
                                className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <LoadingSpinner size="sm" className="text-white" />
                                ) : (
                                    <>
                                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                                            <path fill="currentColor" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                                        </svg>
                                        Connect GCP Account
                                    </>
                                )}
                            </button>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center" aria-hidden="true">
                                    <div className="w-full border-t border-gray-300"></div>
                                </div>
                                <div className="relative flex justify-center text-sm">
                                    <span className="px-2 bg-white text-gray-500 font-mono">INTERNAL PREVIEW</span>
                                </div>
                            </div>

                            <button
                                onClick={async () => {
                                    setIsLoading(true);
                                    try {
                                        const res = await authAPI.demoLogin();
                                        login(res.data.token, res.data.user);
                                        navigate('/dashboard');
                                    } catch (err) {
                                        setError("Test account not configured in backend.");
                                    } finally {
                                        setIsLoading(false);
                                    }
                                }}
                                className="w-full flex justify-center py-2 px-4 border border-indigo-600 rounded-md shadow-sm text-sm font-medium text-indigo-600 bg-white hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                                Test Account with Real GCP Deployment
                            </button>

                            <button
                                onClick={() => setStep(1)}
                                className="w-full text-center text-sm text-gray-500 hover:text-gray-700"
                            >
                                Back to Setup
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
