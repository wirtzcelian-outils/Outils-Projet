import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import Navbar from '../components/Navbar';
import SortableItem from '../components/SortableItem';
import { Share2, Lock } from 'lucide-react';

export default function ListEditor() {
    const { listId } = useParams(); // Can be private or public ID
    const [list, setList] = useState(null);
    const [items, setItems] = useState([]);
    const [isOwner, setIsOwner] = useState(false);

    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    const fetchList = async () => {
        try {
            const res = await axios.get(`/api/lists/${listId}`);
            setList(res.data);
            setItems(res.data.items.sort((a, b) => a.rank - b.rank));
            setIsOwner(res.data.is_owner);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchList();
    }, [listId]);

    const handleDragEnd = async (event) => {
        const { active, over } = event;

        if (active.id !== over.id) {
            setItems((items) => {
                const oldIndex = items.findIndex((item) => item.id === active.id);
                const newIndex = items.findIndex((item) => item.id === over.id);

                const newOrder = arrayMove(items, oldIndex, newIndex);

                // Update ranks locally then sync
                const updatedOrder = newOrder.map((item, index) => ({
                    ...item,
                    rank: index + 1
                }));

                // Sync with backend
                if (isOwner && list.private_id) {
                    axios.put(`/api/lists/${list.private_id}/reorder`, {
                        items: updatedOrder.map(i => ({ id: i.id, rank: i.rank }))
                    });
                }

                return updatedOrder;
            });
        }
    };

    if (!list) return <div className="text-center p-10">Chargement...</div>;

    return (
        <div className="min-h-screen bg-background">
            <Navbar />
            <div className="container mx-auto p-6 max-w-4xl">
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-2">
                            {list.name}
                        </h1>
                        <p className="text-slate-400">
                            {isOwner ? "Mode Édition" : "Mode Lecture Seule"}
                        </p>
                    </div>
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
                            <div className="px-3 py-2 bg-slate-800 rounded border border-slate-700 flex items-center gap-2 text-sm text-slate-400">
                                <Lock size={14} /> Privé
                            </div>
                        </div>
                    )}
                </div>

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
                                <SortableItem key={item.id} id={item.id} item={item} isOwner={isOwner} />
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
