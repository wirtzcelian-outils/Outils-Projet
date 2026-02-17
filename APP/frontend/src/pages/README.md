# Documentation Pages

Ce dossier contient les composants principaux correspondant aux différentes vues (routes) de l'application.

## Fichiers

*   **`Admin.jsx`** : Tableau de bord administrateur (route `/admin`). Permet de :
    *   Lister, modifier et supprimer des utilisateurs.
    *   Gérer les films personnalisés ajoutés par les utilisateurs (suppression).
    *   Exporter et importer les données de la base de données (JSON).
*   **`Auth.jsx`** : Page d'authentification (route `/auth`). Gère à la fois le formulaire de connexion et d'inscription avec une transition animée.
*   **`Dashboard.jsx`** : Tableau de bord utilisateur (route `/dashboard` ou `/`). Permet de :
    *   Voir et créer des listes de films.
    *   Rechercher des films dans la base globale.
    *   Ajouter des films aux listes.
    *   Créer des films personnalisés s'ils n'existent pas.
    *   Gérer sa bio de profil.
*   **`ListEditor.jsx`** : Page de détail et d'édition d'une liste (route `/list/:listId`). Permet de :
    *   Voir les films d'une liste.
    *   Réorganiser les films par glisser-déposer (Drag & Drop).
    *   Ajouter/Modifier des commentaires sur les films.
    *   Partager la liste (lien public).
    *   Supprimer la liste.
