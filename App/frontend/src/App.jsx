import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import Admin from './pages/Admin';
import ListEditor from './pages/ListEditor';
import SplashScreen from './components/SplashScreen';
import { useState, useEffect } from 'react';
import axios from 'axios';

// Composant wrapper pour protéger les routes qui nécessitent une authentification
function PrivateRoute({ children }) {
    const { user, loading } = useAuth();

    // Si l'état d'authentification est encore en chargement, on affiche un message d'attente
    if (loading) return <div>Loading...</div>;

    // Si l'utilisateur n'est pas connecté, on le redirige vers la page d'authentification
    if (!user) return <Navigate to="/auth" />;

    // Si tout est bon, on affiche le composant enfant (la page protégée)
    return children;
}

export default function App() {
    const [isServerReady, setIsServerReady] = useState(false);

    // Effet pour vérifier la santé du serveur backend au démarrage
    useEffect(() => {
        const checkHealth = async () => {
            try {
                // Tente de contacter l'endpoint de santé du backend
                await axios.get('/api/health');
                setIsServerReady(true);
            } catch (error) {
                // Si échec (ex: serveur pas encore UP), on réessaie dans 2 secondes
                setTimeout(checkHealth, 2000);
            }
        };

        checkHealth();
    }, []);

    // Affiche l'écran de chargement tant que le backend n'est pas prêt
    if (!isServerReady) {
        return <SplashScreen />;
    }

    return (
        <Router>
            {/* AuthProvider rend les données d'authentification accessibles à toute l'app */}
            <AuthProvider>
                <Routes>
                    {/* Route publique : Authentification */}
                    <Route path="/auth" element={<Auth />} />

                    {/* Routes protégées : nécessitent d'être connecté */}
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

                    {/* Redirection par défaut vers le dashboard */}
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                </Routes>
            </AuthProvider>
        </Router>
    );
}
