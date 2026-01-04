import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical } from 'lucide-react';

export default function SortableItem({ id, item, isOwner }) {
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
            </div>
            <div className="flex-1">
                <div className="flex items-center gap-2">
                    <span className="text-xl font-bold text-slate-600">#{item.rank}</span>
                    <h4 className="font-bold">{item.movie.title}</h4>
                </div>
                {item.comment && <p className="text-slate-400 text-sm mt-1">{item.comment}</p>}
            </div>
        </div>
    );
}
