import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut } from 'lucide-react';

export default function Navbar() {
    const { logout } = useAuth();
    const navigate = useNavigate();

    // Gère la déconnexion de l'utilisateur
    const handleLogout = () => {
        logout();
        navigate('/auth'); // Redirection vers la page de connexion
    };

    return (
        <nav className="bg-surface border-b border-slate-700 p-4">
            <div className="container mx-auto flex justify-between items-center">
                {/* Logo / Titre de l'application avec lien vers le tableau de bord */}
                <Link to="/dashboard" className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    Classement Ciné
                </Link>

                <div className="flex items-center gap-4">
                    {/* Affichage du nom d'utilisateur s'il est connecté */}
                    {useAuth().user?.username && (
                        <span className="text-slate-300">
                            Bonjour, <span className="text-primary font-semibold">{useAuth().user.username}</span>
                        </span>
                    )}

                    {/* Bouton de déconnexion */}
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
                    >
                        <LogOut size={18} />
                        <span>Déconnexion</span>
                    </button>
                </div>
            </div>
        </nav>
    );
}
