import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

export default function Auth() {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login, register } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (isLogin) {
            const success = await login(username, password);
            if (success) navigate('/dashboard');
            else setError('Identifiants invalides');
        } else {
            const result = await register(username, password);
            if (result.success) {
                // Auto login after register or ask to login? Let's auto login or switch to login
                const loginSuccess = await login(username, password);
                if (loginSuccess) navigate('/dashboard');
                else setIsLogin(true); // Fallback
            } else setError(result.error);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                        Mon Classement Ciné
                    </h1>
                    <p className="text-secondary mt-2">Vos films, vos listes, vos avis.</p>
                </div>

                <motion.div
                    layout
                    className="card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div className="flex mb-6 border-b border-slate-700">
                        <button
                            className={`flex-1 pb-2 font-medium transition-colors ${isLogin ? 'text-primary border-b-2 border-primary' : 'text-secondary hover:text-white'}`}
                            onClick={() => setIsLogin(true)}
                        >
                            Connexion
                        </button>
                        <button
                            className={`flex-1 pb-2 font-medium transition-colors ${!isLogin ? 'text-primary border-b-2 border-primary' : 'text-secondary hover:text-white'}`}
                            onClick={() => setIsLogin(false)}
                        >
                            Inscription
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Pseudo</label>
                            <input
                                type="text"
                                required
                                className="input-field"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Mot de passe</label>
                            <input
                                type="password"
                                required
                                className="input-field"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>

                        {error && <p className="text-red-400 text-sm">{error}</p>}

                        <button type="submit" className="w-full btn-primary mt-6">
                            {isLogin ? 'Se connecter' : "S'inscrire"}
                        </button>
                    </form>
                </motion.div>
            </div>
        </div>
    );
}
