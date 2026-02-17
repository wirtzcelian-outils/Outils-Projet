# Documentation Nginx

Ce dossier contient la configuration du serveur web Nginx.

## Fichiers

*   **`default.conf`** : Fichier de configuration principal pour le site. Il définit les règles de routage (proxy pass vers le backend API, service des fichiers statiques du frontend, gestion des erreurs 404/500).
*   **`html/`** : Dossier contenant les fichiers HTML statiques servis par défaut ou en cas d'erreur.
