# Documentation du Projet

Ce dossier contient l'ensemble du code source de l'application "Classement Ciné".

## Structure du Dossier

*   **`.env`** : Fichier de configuration contenant les variables d'environnement (non versionné généralement) telles que les clés secrètes et les identifiants de base de données.
*   **`docker-compose.yml`** : Fichier de configuration Docker Compose permettant de lancer et d'orchestrer l'ensemble des services de l'application (Backend, Frontend, Base de données) en une seule commande.
*   **`backend/`** : Dossier contenant tout le code source de l'API (serveur Python/Flask).
*   **`frontend/`** : Dossier contenant tout le code source de l'interface utilisateur (client React/Vite).
*   **`mysql/`** : Dossier contenant les configurations ou fichiers de données liés à la base de données MySQL.
*   **`nginx/`** : Dossier contenant la configuration du serveur web Nginx, utilisé comme reverse proxy et pour servir les fichiers statiques en production.
