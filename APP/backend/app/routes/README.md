# Documentation des Routes API

Ce dossier contient les définitions des endpoints de l'API, organisées par modules fonctionnels (Blueprints Flask).

## Fichiers

*   **`__init__.py`** : Initialise le package `routes` et importe les différents Blueprints pour qu'ils soient accessibles par l'application principale.
*   **`admin.py`** : Gère les fonctionnalités administratives (suppression d'utilisateurs, gestion des films personnalisés, export/import de données).
*   **`auth.py`** : Gère l'authentification des utilisateurs (inscription, connexion, génération de Token JWT).
*   **`lists.py`** : Gère les listes de films des utilisateurs (création, modification, ajout/suppression de films, réorganisation).
*   **`movies.py`** : Gère la recherche de films (API externe ou base locale) et la création de films personnalisés.
*   **`profile.py`** : Gère les informations du profil utilisateur, notamment la bio.
