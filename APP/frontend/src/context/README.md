# Documentation Context

Ce dossier contient les contextes React pour la gestion d'état global.

## Fichiers

*   **`AuthContext.jsx`** : Fournit le contexte d'authentification à l'ensemble de l'application. Il gère :
    *   L'état de l'utilisateur connecté (`user`).
    *   Le token JWT (`token`).
    *   Les fonctions de connexion (`login`), d'inscription (`register`) et de déconnexion (`logout`).
    *   La persistance de la session via `localStorage`.
    *   La configuration automatique des en-têtes Authorization d'Axios.
