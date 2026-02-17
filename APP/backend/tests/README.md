# Tests Unitaires Backend

Ce dossier contient l'ensemble des tests automatisés pour l'API Backend, utilisant le framework **pytest**.
Ces tests assurent la stabilité de l'application, la sécurité des routes et la cohérence des données.

## Structure du Dossier

- **`conftest.py`** :  
  Fichier de configuration essentiel. Il contient les "fixtures" (outils de test) partagés, comme la création d'une base de données temporaire en mémoire et le client de test simulé.

- **`test_auth.py`** :  
  Tests liés à l'authentification :
  - Inscription réussie et gestion des doublons (code 409).
  - Connexion réussie (récupération du Token JWT).
  - Rejet des mauvais mots de passe (code 401).

- **`test_lists.py`** :  
  Tests pour la gestion des listes de films :
  - Création de listes (vérification des IDs privés/publics).
  - Isolation des données (un utilisateur ne voit que ses listes).
  - Ajout et suppression de films dans une liste.
  - Suppression complète de liste.

- **`test_models.py`** :  
  Tests unitaires sur les modèles de données (SQLAlchemy) :
  - Vérification du hachage de mot de passe (sécurité).
  - Vérification des relations entre tables (User <-> Listes).

- **`test_admin.py`** :  
  Tests pour les fonctionnalités d'administration :
  - **Sécurité** : Vérifie qu'un utilisateur standard ne peut PA accéder aux routes admin (code 403).
  - Suppression d'utilisateurs par un administrateur.

## Lancer les Tests

Pour exécuter la suite complète de tests, ouvrez un terminal dans le dossier `backend/` et lancez :

```bash
python -m pytest
```

Si tout est vert, le code est stable !
