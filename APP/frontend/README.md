# Documentation Frontend

Ce dossier contient le code source de l'interface utilisateur de l'application, développée avec React et Vite.

## Dossiers et Fichiers

*   **`public/`** : Dossier contenant les actifs statiques accessibles publiquement (images, favicons, etc.).
*   **`src/`** : Dossier contenant tout le code source JavaScript et CSS de l'application.
*   **`Dockerfile`** : Instructions pour construire l'image Docker du frontend.
*   **`index.html`** : Point d'entrée HTML de l'application. C'est ici que le bundle JavaScript est injecté par Vite.
*   **`package.json`** : Fichier de configuration NPM listant les dépendances du projet (React, Tailwind, Axios, etc.) et les scripts de commande (`dev`, `build`).
*   **`postcss.config.js`** : Fichier de configuration pour PostCSS, nécessaire pour le traitement de Tailwind CSS.
*   **`tailwind.config.js`** : Fichier de configuration de Tailwind CSS, définissant le thème, les couleurs personnalisées et les chemins de contenu à analyser.
*   **`vite.config.js`** : Fichier de configuration de Vite, gérant le serveur de développement, le proxy vers le backend et l'optimisation du build.
