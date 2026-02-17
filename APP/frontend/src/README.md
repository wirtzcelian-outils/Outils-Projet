# Documentation Source Frontend

Ce dossier `src` contient l'ensemble de la logique applicative du frontend React.

## Fichiers et Dossiers

*   **`components/`** : Dossier contenant les composants React réutilisables (boutons, cartes, navbar, etc.) qui ne sont pas des pages à part entière.
*   **`context/`** : Dossier contenant les configurations de l'API Context de React, utilisé ici pour gérer l'état global de l'authentification (`AuthContext`).
*   **`pages/`** : Dossier contenant les composants "Vues" ou "Pages" qui correspondent aux différentes routes de l'application (Login, Dashboard, Admin).
*   **`App.jsx`** : Composant racine de l'application. Il définit les routes (via `react-router-dom`) et intègre les fournisseurs de contexte globaux (`AuthProvider`).
*   **`main.jsx`** : Point d'entrée JavaScript. Il est responsable de monter l'application React (`App`) dans l'élément racine du DOM (`#root`).
*   **`index.css`** : Fichier de styles globaux. Il contient notamment les directives d'importation de Tailwind CSS (`@tailwind base`, etc.).
