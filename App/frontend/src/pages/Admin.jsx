import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

// Page d'administration (protégée)
// Permet de gérer les utilisateurs, les films personnalisés, et d'exporter/importer les données
export default function Admin() {
    const [users, setUsers] = useState([]);
    const [customMovies, setCustomMovies] = useState([]);
    const [activeTab, setActiveTab] = useState('users'); // Onglet actif : 'users' ou 'movies'
    const [error, setError] = useState('');
    const { token, logout } = useAuth();

    // États pour les modales et confirmations
    const [showMovieDeleteConfirm, setShowMovieDeleteConfirm] = useState(null);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);
    const [editUsername, setEditUsername] = useState('');
    const [editPassword, setEditPassword] = useState('');

    // Chargement initial des données
    useEffect(() => {
        if (token) {
            fetchUsers();
            fetchCustomMovies();
        }
    }, [token]);

    const fetchUsers = async () => {
        try {
            const response = await axios.get('/api/admin/users', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(response.data);
        } catch (err) {
            console.error("Failed to fetch users", err);
            setError("Impossible de charger les utilisateurs.");
        }
    };

    const fetchCustomMovies = async () => {
        try {
            const response = await axios.get('/api/admin/movies/custom', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setCustomMovies(response.data);
        } catch (err) {
            console.error("Failed to fetch movies", err);
        }
    };

    // Suppression d'un utilisateur
    const handleDelete = async (userId) => {
        if (!window.confirm("Êtes-vous sûr de vouloir supprimer cet utilisateur ? Cette action est irréversible.")) return;

        try {
            await axios.delete(`/api/admin/users/${userId}`);
            setUsers(users.filter(u => u.id !== userId));
        } catch (err) {
            console.error("Failed to delete user", err);
            alert("Erreur lors de la suppression.");
        }
    };

    // Suppression d'un film personnalisé
    const handleDeleteMovie = async () => {
        if (!showMovieDeleteConfirm) return;
        try {
            await axios.delete(`/api/admin/movies/${showMovieDeleteConfirm.id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setShowMovieDeleteConfirm(null);
            fetchCustomMovies(); // Rafraîchir la liste après suppression
        } catch (err) {
            console.error(err);
            alert("Erreur lors de la suppression du film");
        }
    };

    // Ouverture de la modale d'édition utilisateur
    const openEditModal = (user) => {
        setCurrentUser(user);
        setEditUsername(user.username);
        setEditPassword(''); // On ne pré-remplit jamais le mot de passe
        setIsEditModalOpen(true);
    };

    // Soumission de la modification utilisateur
    const handleEditSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = { username: editUsername };
            if (editPassword) data.password = editPassword;

            await axios.put(`/api/admin/users/${currentUser.id}`, data);

            // Mise à jour locale de l'état pour éviter un rechargement
            setUsers(users.map(u => u.id === currentUser.id ? { ...u, username: editUsername } : u));
            setIsEditModalOpen(false);
            alert("Utilisateur mis à jour avec succès.");
        } catch (err) {
            console.error("Failed to update user", err);
            alert(err.response?.data?.msg || "Erreur lors de la mise à jour.");
        }
    };

    // Export des données au format JSON
    const handleExport = async () => {
        try {
            const response = await axios.get('/api/admin/export', {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob', // Important pour télécharger un fichier
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const date = new Date().toISOString().split('T')[0];
            link.setAttribute('download', `backup_cineconnect_${date}.json`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Export failed", err);
            alert("Erreur lors de l'export.");
        }
    };

    // Import des données depuis un fichier JSON
    const handleImport = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (event) => {
            try {
                const jsonData = JSON.parse(event.target.result);
                await axios.post('/api/admin/import', jsonData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                alert("Import réussi ! La page va se rafraîchir.");
                window.location.reload();
            } catch (err) {
                console.error("Import failed", err);
                alert("Erreur lors de l'import : " + (err.response?.data?.msg || err.message));
            }
        };
        reader.readAsText(file);
        e.target.value = ''; // Reset de l'input file
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white p-8">
            <div className="max-w-6xl mx-auto">
                {/* En-tête du Dashboard */}
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Admin Dashboard</h1>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setActiveTab('users')}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'users' ? 'bg-primary text-white' : 'text-slate-400 hover:text-white'}`}
                        >
                            Utilisateurs
                        </button>
                        <button
                            onClick={() => setActiveTab('movies')}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'movies' ? 'bg-primary text-white' : 'text-slate-400 hover:text-white'}`}
                        >
                            Films Ajoutés
                        </button>
                        <button onClick={logout} className="btn-secondary">Déconnexion</button>
                    </div>
                </div>

                {/* Barre d'actions (Export / Import) */}
                <div className="flex gap-4 mb-8">
                    <button onClick={handleExport} className="btn-primary flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                        </svg>
                        Sauvegarder les données
                    </button>
                    <label className="btn-secondary flex items-center gap-2 cursor-pointer">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                        </svg>
                        Importer des données
                        <input type="file" accept=".json" onChange={handleImport} className="hidden" />
                    </label>
                </div>

                {error && <p className="text-red-400 mb-4">{error}</p>}

                {/* Contenu principal : Liste Utilisateurs OU Films Custom */}
                {activeTab === 'users' ? (
                    <div className="card overflow-hidden">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-slate-700 text-slate-400">
                                    <th className="p-4">ID</th>
                                    <th className="p-4">Pseudo</th>
                                    <th className="p-4 text-center">Listes</th>
                                    <th className="p-4">Date création</th>
                                    <th className="p-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr key={user.id} className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                                        <td className="p-4 text-slate-500">#{user.id}</td>
                                        <td className="p-4 font-medium">{user.username}</td>
                                        <td className="p-4 text-center">
                                            <span className="bg-slate-700 px-2 py-1 rounded text-sm">{user.list_count}</span>
                                        </td>
                                        <td className="p-4 text-slate-400 text-sm">
                                            {new Date(user.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="p-4 text-right space-x-2">
                                            <button
                                                onClick={() => openEditModal(user)}
                                                className="text-blue-400 hover:text-blue-300 transition-colors"
                                            >
                                                Éditer
                                            </button>
                                            <button
                                                onClick={() => handleDelete(user.id)}
                                                className="text-red-400 hover:text-red-300 transition-colors"
                                            >
                                                Supprimer
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {users.length === 0 && (
                                    <tr>
                                        <td colSpan="5" className="p-8 text-center text-slate-500">Aucun utilisateur trouvé.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="card overflow-hidden">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-slate-700 text-slate-400">
                                    <th className="p-4">ID</th>
                                    <th className="p-4">Titre</th>
                                    <th className="p-4">Année</th>
                                    <th className="p-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {customMovies.length === 0 ? (
                                    <tr>
                                        <td colSpan="4" className="p-8 text-center text-slate-500">Aucun film ajouté par les utilisateurs.</td>
                                    </tr>
                                ) : (
                                    customMovies.map(movie => (
                                        <tr key={movie.id} className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                                            <td className="p-4 text-slate-500">#{movie.id}</td>
                                            <td className="p-4 font-medium">{movie.title}</td>
                                            <td className="p-4 text-slate-400">{movie.release_date}</td>
                                            <td className="p-4 text-right">
                                                <button
                                                    onClick={() => setShowMovieDeleteConfirm(movie)}
                                                    className="text-red-400 hover:text-red-300 transition-colors"
                                                >
                                                    Supprimer
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Modale de confirmation de suppression de film */}
                {showMovieDeleteConfirm && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
                        <div className="card w-full max-w-md border border-red-500/20">
                            <h3 className="text-xl font-bold mb-2 text-red-400">Supprimer ce film ?</h3>
                            <p className="text-slate-300 mb-6">
                                Êtes-vous sûr de vouloir supprimer <strong>{showMovieDeleteConfirm.title}</strong> ?
                                <br />
                                <span className="text-sm text-slate-500">Cela le retirera de TOUTES les listes des utilisateurs.</span>
                            </p>
                            <div className="flex justify-end gap-3">
                                <button
                                    onClick={() => setShowMovieDeleteConfirm(null)}
                                    className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
                                >
                                    Annuler
                                </button>
                                <button
                                    onClick={handleDeleteMovie}
                                    className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                                >
                                    Supprimer définitivement
                                </button>
                            </div>
                        </div>
                    </div>
                )}

            </div>

            {/* Modale d'édition utilisateur */}
            {isEditModalOpen && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
                    <div className="card w-full max-w-md">
                        <h2 className="text-2xl font-bold mb-4">Modifier l'utilisateur</h2>
                        <form onSubmit={handleEditSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Pseudo</label>
                                <input
                                    type="text"
                                    className="input-field"
                                    value={editUsername}
                                    onChange={(e) => setEditUsername(e.target.value)}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Nouveau mot de passe (optionnel)</label>
                                <input
                                    type="password"
                                    className="input-field"
                                    value={editPassword}
                                    onChange={(e) => setEditPassword(e.target.value)}
                                    placeholder="Laisser vide pour ne pas changer"
                                    autoComplete="new-password"
                                />
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsEditModalOpen(false)}
                                    className="text-slate-400 hover:text-white px-4 py-2"
                                >
                                    Annuler
                                </button>
                                <button type="submit" className="btn-primary">
                                    Enregistrer
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
