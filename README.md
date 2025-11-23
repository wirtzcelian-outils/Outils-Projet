Mon Classement Ciné

Projet d’application de classement de films

Du débat entre amis aux recommandations personnalisées, vos listes de films méritent mieux qu’un carnet ou un bloc-notes : cette application les transforme en classements vivants, partageables et toujours accessibles !


Présentation du projet :

Cette application permet à chaque utilisateur de se créer un compte et de se connecter (gestion des identifiants conforme au RGPD si possible). Après authentification, l’utilisateur accède à une bibliothèque de films (liste de titres récupérés via une API externe). 

Il peut créer des listes de films personnalisées à partir de ces propositions, ordonner librement les films dans chaque liste, puis partager ou dupliquer ses listes. 

Chaque liste dispose d’un identifiant de lecture public (pour le partager en lecture seule ou le copier pour soi) et d’un identifiant privé (pour le modifier). Cela offre à l’utilisateur la possibilité de partager son classement avec d’autres sans donner accès à la gestion interne de la liste.




Fonctionnalités clés

Authentification sécurisée (RGPD) : inscription et connexion par email/mot de passe (haché), gestion du droit à l’oubli.

Catalogue de films (API) : consultation d’une base de films fournie par des APIs externes.

Création et édition de listes : l’utilisateur peut composer plusieurs listes de films, modifier leur ordre, ajouter ou retirer des titres.

Classement des films : possibilité de réordonner les films à l’intérieur d’une liste selon ses préférences.

Partage et duplication des listes : chaque liste possède un identifiant public (pour partager en lecture seule) et un identifiant privé (pour gérer ou copier la liste).




Technologies et dépendances

Backend en Python avec Flask en framework web fournissant une API REST sécurisée.

Frontend (application) : interface web ou mobile utilisant React, pour interagir avec l’utilisateur.

Base de données MongoDB : serveur orienté documents pour stocker utilisateurs, films et listes.



APIs externes : intégration d’APIs de films pour récupérer les titres et métadonnées de films.

Docker & Docker Compose : pour conteneuriser l’application (backend Python) et la base de données, garantissant un déploiement facile et consistant.

Bibliothèques Python : par exemple PyMongo (pour MongoDB), un module d’authentification (JWT ou Flask-Login), bcrypt/Argon2 (hash des mots de passe), etc.

Variables d’environnement : pour stocker en sécurité les clés d’API et les mots de passe (par exemple dans un fichier .env utilisé par Docker).




Plus de détails :

La base comprendra typiquement plusieurs collections : une collection Users (utilisateurs avec email et mot de passe haché), une collection Films (stockant la liste les titres et identifiants de films, avec aussi une image si cela est possible) et une collection Lists (chaque document listant les films et leur classement, ainsi que les identifiants de partage et identifiants privé). Cette organisation permet des requêtes simples (par exemple retrouver les listes d’un utilisateur ou récupérer une liste via son identifiant public) tout en restant très flexible.

Authentification et RGPD

La gestion des comptes utilisateurs doit respecter les bonnes pratiques de sécurité et le RGPD dans la mesure du possible. Les mots de passe seront hachés (bcrypt ou Argon2) avant stockage, et jamais conservés en clair.
L’application devra aussi implémenter un mécanisme de suppression de compte (droit à l’oubli) pour effacer toutes les données personnelles d’un utilisateur sur simple demande. Les sessions peuvent être gérées via des tokens JWT pour sécuriser les appels API (chaque requête authentifiée portant un token valide, à voir si réalisable dans le temps imparti).

Conteneurisation (Docker) et déploiement

Docker est essentiel pour garantir que le développement et le déploiement soient reproductibles et isolés. En conteneurisant l’application, on s’assure que le service Python et la base MongoDB s’exécutent dans des environnements identiques (mêmes versions, mêmes dépendances).
. Le Docker Compose simplifie grandement la gestion multi-conteneurs : on peut « define and configure all your services in a single docker-compose.yml file », ce qui permet de lancer l’ensemble du projet (backend + base) avec une seule commande

. Cela signifie qu’il suffira de mettre à jour le fichier docker-compose.yml pour déclarer les conteneurs nécessaires (application Python, MongoDB, éventuellement front-end...), puis exécuter docker-compose up pour démarrer tous les services en parallèle.

