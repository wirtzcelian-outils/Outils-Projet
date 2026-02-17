# Documentation Backend

Ce dossier contient le code de l'API RESTful de l'application, développée avec Python et Flask.

## Fichiers

*   **`app/`** : Package Python principal contenant le cœur de l'application (modèles, routes, configuration).
*   **`app.py`** : Point d'entrée principal de l'application. C'est ce fichier qui est exécuté pour démarrer le serveur Flask.
*   **`Dockerfile`** : Fichier décrivant comment construire l'image Docker pour le service backend.
*   **`requirements.txt`** : Liste de toutes les bibliothèques Python nécessaires au fonctionnement de l'application.
*   **`update_movies.py`** : Script utilitaire autonome permettant d'initialiser ou de mettre à jour la base de données des films (par exemple, pour le seeding initial).
