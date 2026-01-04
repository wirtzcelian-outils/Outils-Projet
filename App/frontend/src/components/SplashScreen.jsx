import React from 'react';
import { Film } from 'lucide-react';

export default function SplashScreen() {
    return (
        <div className="fixed inset-0 bg-background flex flex-col items-center justify-center z-50">
            <div className="flex flex-col items-center animate-pulse">
                <Film size={64} className="text-primary mb-4" />
                <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent mb-2">
                    Classement Ciné
                </h1>
                <p className="text-slate-400 text-sm">Démarrage du serveur...</p>
            </div>

            {/* Loading Spinner */}
            <div className="mt-8 flex gap-2">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
        </div>
    );
}
