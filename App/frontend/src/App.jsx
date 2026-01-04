import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import Admin from './pages/Admin';
import ListEditor from './pages/ListEditor';
import SplashScreen from './components/SplashScreen';
import { useState, useEffect } from 'react';
import axios from 'axios';

function PrivateRoute({ children }) {
    const { user, loading } = useAuth();
    if (loading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/auth" />;
    return children;
}

export default function App() {
    const [isServerReady, setIsServerReady] = useState(false);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                // Try to hit the backend health endpoint
                await axios.get('/api/health'); // Ensure backend has this endpoint or use a lightweight one
                setIsServerReady(true);
            } catch (error) {
                // If it fails, retry in 2 seconds
                setTimeout(checkHealth, 2000);
            }
        };

        checkHealth();
    }, []);

    if (!isServerReady) {
        return <SplashScreen />;
    }

    return (
        <Router>
            <AuthProvider>
                <Routes>
                    <Route path="/auth" element={<Auth />} />
                    <Route path="/dashboard" element={
                        <PrivateRoute>
                            <Dashboard />
                        </PrivateRoute>
                    } />
                    <Route path="/admin" element={
                        <PrivateRoute>
                            <Admin />
                        </PrivateRoute>
                    } />
                    <Route path="/list/:listId" element={<ListEditor />} />
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                </Routes>
            </AuthProvider>
        </Router>
    );
}
