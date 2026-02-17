import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Création du contexte React pour l'authentification
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    // Au chargement du composant, on vérifie si une session est déjà stockée
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken) {
            setToken(storedToken);
            if (storedUser) {
                try {
                    setUser(JSON.parse(storedUser));
                } catch (e) {
                    // Si erreur de parsing, on garde au moins le token
                    setUser({ token: storedToken });
                }
            } else {
                setUser({ token: storedToken });
            }
            // Configuration globale d'Axios pour inclure le token dans toutes les requêtes futures
            axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        } else {
            // Nettoyage si pas de token
            delete axios.defaults.headers.common['Authorization'];
            setUser(null);
        }
        setLoading(false);
    }, []);

    const login = async (username, password) => {
        try {
            // Appel API pour se connecter
            const response = await axios.post('/api/auth/login', {}, { params: { username, password } });

            const newToken = response.data.access_token;
            // Fusionne les infos utilisateur reçues avec le token
            const userData = { ...response.data.user, token: newToken };

            // Mise à jour de l'état local et du stockage persistent
            setToken(newToken);
            localStorage.setItem('token', newToken);
            localStorage.setItem('user', JSON.stringify(userData));

            // Mise à jour des headers Axios
            axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
            setUser(userData);

            return userData;
        } catch (error) {
            console.error("Login failed", error);
            return false;
        }
    };

    const register = async (username, password) => {
        try {
            // Appel API pour l'inscription
            await axios.post('/api/auth/register', {}, { params: { username, password } });
            return { success: true };
        } catch (error) {
            console.error("Registration failed", error);
            const message = error.response?.data?.msg || "Erreur lors de l'inscription";
            return { success: false, error: message };
        }
    };

    const logout = () => {
        // Nettoyage complet de l'état et du stockage lors de la déconnexion
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        delete axios.defaults.headers.common['Authorization'];
    };

    return (
        // Fournit les fonctions et l'état d'auth aux composants enfants
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

// Hook personnalisé pour faciliter l'accès au contexte d'authentification
export const useAuth = () => useContext(AuthContext);
