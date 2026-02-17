import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Point d'entrée de l'application React
// C'est ici que l'application est "montée" dans la balise <div id="root"> du fichier index.html
ReactDOM.createRoot(document.getElementById('root')).render(
    // StrictMode active des vérifications supplémentaires et des avertissements en développement
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
