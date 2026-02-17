# Documentation de l'Application Flask

Ce dossier `app` est le package principal de l'application backend. Il structure la logique de l'API.

## Fichiers et Dossiers

*   **`__init__.py`** : Fichier d'initialisation du package. Il crée l'instance de l'application Flask (`create_app`), configure les extensions (Base de données, CORS, JWT, Migration) et enregistre les différents Blueprints (routes).
*   **`config.py`** : Contient la classe `Config` qui définit les paramètres de l'application (clés secrètes, URI de connexion à la base de données), en les récupérant souvent depuis les variables d'environnement.
*   **`models.py`** : Définit les modèles de données SQLAlchemy qui structurent la base de données (ex: `User`, `Movie`, `List`, `ListItem`).
*   **`routes/`** : Dossier contenant les différents modules de routes (endpoints API) organisés par fonctionnalité.
*   **`services/`** : Dossier destiné à contenir la logique métier complexe ou les services externes (actuellement principalement structurel).
