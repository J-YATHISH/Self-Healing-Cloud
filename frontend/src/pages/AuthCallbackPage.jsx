import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from '../components/common/LoadingSpinner';

const AuthCallbackPage = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState('processing');

    useEffect(() => {
        console.log('🔍 AuthCallbackPage mounted');
        console.log('📍 Current URL:', window.location.href);

        const token = searchParams.get('token');
        const error = searchParams.get('error');
        const message = searchParams.get('message');

        console.log('🎫 Token present:', !!token);
        console.log('❌ Error present:', !!error);

        if (token) {
            // OAuth success - decode user data from token
            try {
                console.log('📦 Decoding token...');
                const userData = JSON.parse(atob(token));
                console.log('✅ User data decoded:', userData);

                // Retrieve project_id from sessionStorage (stored in AuthPage)
                const storedProjectId = sessionStorage.getItem('oauth_project_id');
                console.log('� Retrieved project_id from session:', storedProjectId);

                setStatus('success');

                // Store token and user data
                const finalUserData = {
                    name: userData.name || "SRE User",
                    email: userData.email || "",
                    id: userData.user_id || "default_user",
                    projectId: storedProjectId || userData.projectId || "PRJ-DEFAULT"
                };

                console.log('💾 Calling login with final user data:', finalUserData);
                login(token, finalUserData);

                console.log('✅ Login completed');

                // Use a hard redirect to ensure the entire app state is refreshed
                // with the new token and user data, avoiding the "stuck" state.
                console.log('🔄 Performing hard redirect to /dashboard...');
                window.location.href = '/dashboard';
            } catch (err) {
                console.error('❌ Failed to decode token:', err);
                setStatus('error');
                navigate('/auth?error=invalid_token', { replace: true });
            }
        } else if (error) {
            // OAuth failed
            console.error('❌ OAuth error:', error, message);
            setStatus('error');

            setTimeout(() => {
                navigate('/auth?error=' + error, { replace: true });
            }, 2000);
        } else {
            // No token or error - something went wrong
            setStatus('error');
            setTimeout(() => {
                navigate('/auth', { replace: true });
            }, 2000);
        }
    }, [searchParams, login, navigate]);

    return (
        <div className="min-h-screen bg-obsidian flex items-center justify-center">
            <div className="text-center">
                {status === 'processing' && (
                    <>
                        <LoadingSpinner size="lg" />
                        <p className="mt-4 text-gray-400">Completing authentication...</p>
                    </>
                )}
                {status === 'success' && (
                    <div className="flex flex-col items-center">
                        <LoadingSpinner size="lg" />
                        <p className="mt-4 text-gray-400 font-mono text-xs uppercase tracking-widest animate-pulse">
                            Establishing Session...
                        </p>
                    </div>
                )}
                {status === 'error' && (
                    <>
                        <div className="w-16 h-16 bg-alert-red/20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-alert-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-bold text-gray-100">Authentication Failed</h2>
                        <p className="text-gray-400 mt-2">Redirecting back to login...</p>
                    </>
                )}
            </div>
        </div>
    );
};

export default AuthCallbackPage;
