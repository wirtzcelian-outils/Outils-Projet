import { useState } from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, Trash2, Pencil, Check, X } from 'lucide-react';

export default function SortableItem({ id, item, isOwner, onRemove, onUpdate }) {
    const [isEditing, setIsEditing] = useState(false);
    const [commentDraft, setCommentDraft] = useState(item.comment || "");

    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
    } = useSortable({ id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    const handleSaveComment = () => {
        onUpdate(id, { comment: commentDraft });
        setIsEditing(false);
    };

    const handleCancelComment = () => {
        setCommentDraft(item.comment || "");
        setIsEditing(false);
    };

    return (
        <div ref={setNodeRef} style={style} className="bg-surface p-4 mb-2 rounded-lg border border-slate-700 flex items-center gap-4 group">
            {isOwner && (
                <div {...attributes} {...listeners} className="cursor-grab text-slate-500 hover:text-white">
                    <GripVertical size={20} />
                </div>
            )}
            <div className="w-12 h-18 bg-slate-800 rounded shrink-0 overflow-hidden">
                {item.movie.poster_path ? (
                    <img
                        src={item.movie.poster_path.startsWith('http') ? item.movie.poster_path : `https://image.tmdb.org/t/p/w200${item.movie.poster_path}`}
                        alt={item.movie.title}
                        className="w-full h-full object-cover"
                    />
                ) : (
                    <div className="w-full h-full bg-slate-700" />
                )}
            </div >
            <div className="flex-1">
                <div className="flex items-center gap-2">
                    <span className="text-xl font-bold text-slate-600">#{item.rank}</span>
                    <h4 className="font-bold">{item.movie.title}</h4>
                </div>

                {isEditing ? (
                    <div className="mt-2 flex gap-2">
                        <textarea
                            className="bg-slate-800 border-slate-700 text-sm p-2 rounded w-full resize-none focus:outline-none focus:border-primary"
                            value={commentDraft}
                            onChange={(e) => setCommentDraft(e.target.value)}
                            placeholder="Ajouter un commentaire..."
                            rows={2}
                            autoFocus
                        />
                        <div className="flex flex-col gap-1">
                            <button
                                onClick={handleSaveComment}
                                className="p-1 bg-primary/20 text-primary hover:bg-primary/30 rounded"
                            >
                                <Check size={16} />
                            </button>
                            <button
                                onClick={handleCancelComment}
                                className="p-1 bg-slate-700 text-slate-400 hover:bg-slate-600 rounded"
                            >
                                <X size={16} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div
                        className="group/comment relative cursor-pointer"
                        onDoubleClick={() => isOwner && setIsEditing(true)}
                    >
                        {item.comment ? (
                            <p className="text-slate-400 text-sm mt-1 whitespace-pre-wrap">{item.comment}</p>
                        ) : (
                            isOwner && <p className="text-slate-600 text-xs mt-1 italic opacity-0 group-hover:opacity-100 transition-opacity">Double-cliquez pour ajouter un commentaire...</p>
                        )}
                    </div>
                )}
            </div>

            {isOwner && (
                <div className="flex gap-1">
                    {!isEditing && (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="p-2 text-slate-500 hover:text-primary hover:bg-primary/10 rounded transition-colors"
                            title="Modifier le commentaire"
                        >
                            <Pencil size={18} />
                        </button>
                    )}
                    <button
                        onClick={() => onRemove(item.id)}
                        className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                        title="Retirer de la liste"
                    >
                        <Trash2 size={18} />
                    </button>
                </div>
            )}
        </div>
    );
}
