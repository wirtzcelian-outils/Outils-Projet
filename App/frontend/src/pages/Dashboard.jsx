import { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import { Link } from 'react-router-dom';
import { Search, Plus, Film } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Dashboard() {
    const [query, setQuery] = useState('');
    const [releaseDate, setReleaseDate] = useState('');
    const [movies, setMovies] = useState([]);
    const [myLists, setMyLists] = useState([]);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newListName, setNewListName] = useState('');
    const [selectedMovie, setSelectedMovie] = useState(null);

    const searchMovies = async (e) => {
        e.preventDefault();
        // Allow empty search to get default library
        try {
            const res = await axios.get(`/api/movies/search?query=${query}&year=${releaseDate}`);
            setMovies(res.data.results || []);
        } catch (err) {
            console.error(err);
        }
    };

    // Initial load of library
    useEffect(() => {
        searchMovies({ preventDefault: () => { } });
    }, []);

    const createCustomMovie = async () => {
        if (!query) return;
        try {
            // If search yielded nothing or user wants to force create
            const res = await axios.post('/api/movies/', { title: query, release_date: releaseDate });
            // Add to results immediately
            setMovies([res.data, ...movies]);
            alert(`Film "${res.data.title}" créé ! Vous pouvez maintenant l'ajouter.`);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchMyLists = async () => {
        try {
            const res = await axios.get('/api/lists/mine');
            setMyLists(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const createList = async () => {
        try {
            await axios.post('/api/lists/', { name: newListName });
            setNewListName('');
            setShowCreateModal(false);
            fetchMyLists();
        } catch (err) {
            console.error(err);
        }
    };

    const addMovieToList = async (listPrivateId) => {
        if (!selectedMovie) return;
        try {
            await axios.post(`/api/lists/${listPrivateId}/items`, {
                movie_id: selectedMovie.id,
                title: selectedMovie.title,
                poster_path: selectedMovie.poster_path
            });
            alert(`"${selectedMovie.title}" ajouté à la liste !`);
            setSelectedMovie(null);
            fetchMyLists(); // Refresh lists to update item counts
        } catch (err) {
            console.error(err);
            alert('Erreur lors de l\'ajout du film à la liste.');
        }
    };

    useEffect(() => {
        fetchMyLists();
    }, []);

    return (
        <div className="min-h-screen bg-background relative">
            <Navbar />
            <div className="container mx-auto p-6">

                {/* Lists Section */}
                <div className="mb-10">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-2xl font-bold">Mes Listes</h2>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="btn-primary flex items-center gap-2"
                        >
                            <Plus size={18} /> Nouvelle Liste
                        </button>
                    </div>

                    {showCreateModal && (
                        <div className="mb-6 p-4 bg-surface rounded-xl border border-slate-700 flex gap-2">
                            <input
                                autoFocus
                                className="input-field"
                                placeholder="Nom de la liste"
                                value={newListName}
                                onChange={(e) => setNewListName(e.target.value)}
                            />
                            <button onClick={createList} className="btn-primary">Créer</button>
                            <button onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-slate-400 hover:text-white">Annuler</button>
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {myLists.map(list => (
                            <Link to={`/list/${list.private_id}`} key={list.id}>
                                <motion.div whileHover={{ scale: 1.02 }} className="card hover:border-primary transition-colors cursor-pointer h-full">
                                    <h3 className="font-bold text-lg mb-2">{list.name}</h3>
                                    <p className="text-slate-400 text-sm">{list.item_count} films</p>
                                </motion.div>
                            </Link>
                        ))}
                    </div>
                </div>

                {/* Search Section */}
                <div>
                    <h2 className="text-2xl font-bold mb-4">Bibliothèque Cine</h2>
                    <form onSubmit={searchMovies} className="flex gap-2 mb-6">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                            <input
                                className="input-field pl-10"
                                placeholder="Rechercher ou Créer un film..."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                            />
                        </div>
                        <input
                            type="text"
                            className="input-field w-32"
                            placeholder="Année"
                            value={releaseDate}
                            onChange={(e) => setReleaseDate(e.target.value)}
                        />
                        <button type="submit" className="btn-primary">Rechercher</button>
                        <button type="button" onClick={createCustomMovie} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white font-medium">
                            Créer
                        </button>
                    </form>

                    {movies.length === 0 && (
                        <div className="text-center text-slate-500 py-10">
                            Aucun film trouvé. Cliquez sur "Créer" pour l'ajouter à la bibliothèque.
                        </div>
                    )}

                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {movies.map(movie => (
                            <div key={movie.id} className="relative group bg-surface rounded-lg overflow-hidden border border-slate-700">
                                {movie.poster_path ? (
                                    <img
                                        src={movie.poster_path.startsWith('http') ? movie.poster_path : `https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                        alt={movie.title}
                                        className="w-full h-auto aspect-[2/3] object-cover"
                                    />
                                ) : (
                                    <div className="w-full aspect-[2/3] bg-slate-800 flex items-center justify-center">
                                        <Film size={32} className="text-slate-600" />
                                    </div>
                                )}
                                <div className="p-3">
                                    <h4 className="font-medium text-sm line-clamp-1" title={movie.title}>{movie.title}</h4>
                                    <p className="text-xs text-slate-500">{movie.release_date?.split('-')[0] || 'N/A'}</p>
                                </div>

                                {/* Hover Overlay */}
                                <div className="absolute inset-0 bg-black/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center p-4">
                                    <button
                                        onClick={() => setSelectedMovie(movie)}
                                        className="btn-primary w-full text-sm"
                                    >
                                        Ajouter à une liste
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Add to List Modal */}
                {selectedMovie && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-surface p-6 rounded-xl w-full max-w-md border border-slate-700">
                            <h3 className="text-xl font-bold mb-4">Ajouter "{selectedMovie.title}" à...</h3>
                            <div className="space-y-2 max-h-60 overflow-y-auto">
                                {myLists.map(list => (
                                    <button
                                        key={list.id}
                                        onClick={() => addMovieToList(list.private_id)}
                                        className="w-full text-left p-3 hover:bg-slate-700 rounded transition-colors flex justify-between items-center"
                                    >
                                        <span>{list.name}</span>
                                        <span className="text-xs text-slate-400">{list.item_count} films</span>
                                    </button>
                                ))}
                            </div>
                            <button
                                onClick={() => setSelectedMovie(null)}
                                className="mt-4 w-full py-2 text-slate-400 hover:text-white"
                            >
                                Annuler
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
