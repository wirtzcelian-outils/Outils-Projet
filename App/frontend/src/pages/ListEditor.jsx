import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import Navbar from '../components/Navbar';
import SortableItem from '../components/SortableItem';
import { Share2, Lock, Pencil, Check, X, Trash2 } from 'lucide-react';

// Page d'édition / visualisation d'une liste
// Gère le Drag & Drop, la modification du nom, et l'ajout de commentaires
export default function ListEditor() {
    const { listId } = useParams(); // Peut être un ID public ou privé
    const navigate = useNavigate();
    const [list, setList] = useState(null);
    const [items, setItems] = useState([]);
    const [isOwner, setIsOwner] = useState(false); // Détermine les droits d'édition

    // États pour le renommage de la liste
    const [isEditingName, setIsEditingName] = useState(false);
    const [listNameDraft, setListNameDraft] = useState('');

    // Configuration des capteurs pour le Drag & Drop (Souris, Tactile, Clavier)
    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    // Chargement des détails de la liste
    const fetchList = async () => {
        try {
            const res = await axios.get(`/api/lists/${listId}`);
            setList(res.data);
            setItems(res.data.items.sort((a, b) => a.rank - b.rank)); // Tri par rang
            setIsOwner(res.data.is_owner);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchList();
    }, [listId]);

    // Gestion de la fin du glisser-déposer
    const handleDragEnd = async (event) => {
        const { active, over } = event;

        if (active.id !== over.id) {
            setItems((items) => {
                const oldIndex = items.findIndex((item) => item.id === active.id);
                const newIndex = items.findIndex((item) => item.id === over.id);

                const newOrder = arrayMove(items, oldIndex, newIndex);

                // Recalcul des rangs
                const updatedOrder = newOrder.map((item, index) => ({
                    ...item,
                    rank: index + 1
                }));

                // Sauvegarde du nouvel ordre si propriétaire
                if (isOwner && list.private_id) {
                    axios.put(`/api/lists/${list.private_id}/reorder`, {
                        items: updatedOrder.map(i => ({ id: i.id, rank: i.rank }))
                    });
                }

                return updatedOrder;
            });
        }
    };

    // Suppression d'un film de la liste
    const handleRemoveItem = async (itemId) => {
        if (!confirm('Voulez-vous vraiment retirer ce film de la liste ?')) return;

        try {
            await axios.delete(`/api/lists/${list.private_id}/items/${itemId}`);
            setItems(items.filter(item => item.id !== itemId));
        } catch (err) {
            console.error("Failed to remove item", err);
            alert("Erreur lors de la suppression");
        }
    };

    // Mise à jour d'un item (ex: commentaire)
    const handleUpdateItem = async (itemId, newData) => {
        try {
            await axios.put(`/api/lists/${list.private_id}/items/${itemId}`, newData);
            setItems(items.map(item =>
                item.id === itemId ? { ...item, ...newData } : item
            ));
        } catch (err) {
            console.error("Failed to update item", err);
            alert("Erreur lors de la modification");
        }
    };

    // Renommage de la liste
    const handleUpdateListName = async () => {
        if (!listNameDraft.trim()) {
            alert('Le nom ne peut pas être vide');
            return;
        }
        try {
            await axios.put(`/api/lists/${list.private_id}`, { name: listNameDraft });
            setList({ ...list, name: listNameDraft });
            setIsEditingName(false);
        } catch (err) {
            console.error("Failed to update list name", err);
            alert("Erreur lors de la modification du nom");
        }
    };

    // Suppression complète de la liste
    const handleDeleteList = async () => {
        if (!confirm('Voulez-vous vraiment supprimer cette liste ? Cette action est irréversible.')) return;

        try {
            await axios.delete(`/api/lists/${list.private_id}`);
            alert('Liste supprimée avec succès');
            navigate('/');
        } catch (err) {
            console.error("Failed to delete list", err);
            alert("Erreur lors de la suppression de la liste");
        }
    };

    if (!list) return <div className="text-center p-10">Chargement...</div>;

    return (
        <div className="min-h-screen bg-background">
            <Navbar />
            <div className="container mx-auto p-6 max-w-4xl">
                {/* En-tête de liste (Nom et Actions) */}
                <div className="flex justify-between items-start mb-8">
                    <div className="flex-1">
                        {isEditingName && isOwner ? (
                            <div className="flex items-center gap-2 mb-2">
                                <input
                                    type="text"
                                    className="text-3xl font-bold bg-slate-800 border border-primary rounded px-2 py-1 focus:outline-none"
                                    value={listNameDraft}
                                    onChange={(e) => setListNameDraft(e.target.value)}
                                    autoFocus
                                />
                                <button
                                    onClick={handleUpdateListName}
                                    className="p-2 bg-primary/20 text-primary hover:bg-primary/30 rounded"
                                >
                                    <Check size={20} />
                                </button>
                                <button
                                    onClick={() => {
                                        setIsEditingName(false);
                                        setListNameDraft(list.name);
                                    }}
                                    className="p-2 bg-slate-700 text-slate-400 hover:bg-slate-600 rounded"
                                >
                                    <X size={20} />
                                </button>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 mb-2">
                                <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                                    {list.name}
                                </h1>
                                {isOwner && (
                                    <button
                                        onClick={() => {
                                            setListNameDraft(list.name);
                                            setIsEditingName(true);
                                        }}
                                        className="p-1 text-slate-500 hover:text-primary transition-colors"
                                        title="Renommer la liste"
                                    >
                                        <Pencil size={18} />
                                    </button>
                                )}
                            </div>
                        )}
                        <p className="text-slate-400">
                            {isOwner ? "Mode Édition" : "Mode Lecture Seule"}
                        </p>
                    </div>

                    {/* Actions de partage et suppression */}
                    {isOwner && (
                        <div className="flex gap-2">
                            <button
                                className="btn-primary flex items-center gap-2"
                                onClick={() => {
                                    navigator.clipboard.writeText(`${window.location.origin}/list/${list.public_id}`);
                                    alert('Lien public copié !');
                                }}
                            >
                                <Share2 size={18} /> Partager
                            </button>
                            <button
                                className="px-3 py-2 bg-red-500/20 text-red-500 hover:bg-red-500/30 rounded border border-red-500/50 flex items-center gap-2 transition-colors"
                                onClick={handleDeleteList}
                                title="Supprimer la liste"
                            >
                                <Trash2 size={18} /> Supprimer
                            </button>
                            <div className="px-3 py-2 bg-slate-800 rounded border border-slate-700 flex items-center gap-2 text-sm text-slate-400">
                                <Lock size={14} /> Privé
                            </div>
                        </div>
                    )}
                </div>

                {/* Liste triable */}
                <DndContext
                    sensors={sensors}
                    collisionDetection={closestCenter}
                    onDragEnd={handleDragEnd}
                >
                    <SortableContext
                        items={items.map(i => i.id)}
                        strategy={verticalListSortingStrategy}
                        disabled={!isOwner}
                    >
                        <div className="space-y-4">
                            {items.map((item) => (
                                <SortableItem
                                    key={item.id}
                                    id={item.id}
                                    item={item}
                                    isOwner={isOwner}
                                    onRemove={handleRemoveItem}
                                    onUpdate={handleUpdateItem}
                                />
                            ))}
                        </div>
                    </SortableContext>
                </DndContext>

                {items.length === 0 && (
                    <div className="text-center py-20 border-2 border-dashed border-slate-800 rounded-xl text-slate-500">
                        Cette liste est vide. {isOwner && "Recherchez des films pour les ajouter !"}
                    </div>
                )}
            </div>
        </div>
    );
}
