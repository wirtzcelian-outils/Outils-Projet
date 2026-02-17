Mon Classement Ciné :



Projet d’application de classement de films

Du débat entre amis aux recommandations personnalisées, vos listes de films méritent mieux qu’un carnet ou un bloc-notes : cette application les transforme en classements vivants, partageables et toujours accessibles !



Présentation du projet :

Cette application permet à chaque utilisateur de se créer un compte et de se connecter. Après authentification, l’utilisateur accède à une bibliothèque de films (liste de titres récupérés via une API externe).

Il peut créer des listes de films personnalisées à partir de ces propositions, ordonner librement les films dans chaque liste, puis partager ou dupliquer ses listes.

Chaque liste dispose d’un identifiant de lecture public (pour le partager en lecture seule ou le copier pour soi) et d’un identifiant privé (pour le modifier). Cela offre à l’utilisateur la possibilité de partager son classement avec d’autres sans donner accès à la gestion interne de la liste.







Fonctionnalités clés :



Authentification sécurisée : inscription et connexion par username/mot de passe.

Catalogue de films : consultation d’une base de films fournie par une BD externe.

Création et édition de listes : l’utilisateur peut composer plusieurs listes de films, modifier leur ordre, ajouter ou retirer des titres.

Classement des films : possibilité de réordonner les films à l’intérieur d’une liste selon ses préférences.

Partage et duplication des listes : chaque liste possède un identifiant public (pour partager en lecture seule) et un identifiant privé (pour gérer ou copier la liste).
Création de films : l’utilisateur peut créer un ou plusieurs films dans la base de données (par contre sans image)

Bio de l'utilisateur : chaque utilisateur à sa biographie personnelle.

Compte administrateur : il existe un compte administrateur (voir .env pour le configurer), il peut supprimer des users, des films créés…

Import / Export des données : l'administrateur peut importer et exporter des données

Changement mot de passe : Un mot de passe oublié ? L'administrateur peut en donner un nouveau (il n'a pas accès à l'ancien)







Conteneurisation (Docker) et déploiement :
https://hub.docker.com/u/tempddaw
(identifiant Dockerhub = testddaw)



Docker est essentiel pour garantir que le développement et le déploiement soient reproductibles et isolés. En conteneurisant l’application, on s’assure que le service Python et la base MySQL s’exécutent dans des environnements identiques (mêmes versions, mêmes dépendances).
Le Docker Compose simplifie grandement la gestion multi-conteneurs : on peut « define and configure all your services in a single docker-compose.yml file », ce qui permet de lancer l’ensemble du projet (backend + base) avec une seule commande.

Cela signifie qu’il suffit de mettre à jour le fichier docker-compose.yml pour déclarer les conteneurs nécessaires (application Python, MySQL, front-end...), puis exécuter docker-compose up pour démarrer tous les services en parallèle.



Pour déployer l'application il suffit de suivre les étapes suivantes :

1\)

install docker

(exemple suivre docs.docker.com/engine/install/Ubuntu) --> Dépend de l'OS

(si vous utiliser Ubuntu faire les commandes des parties 1 et 2)



2\) (probablement pas exactement pareil si vous avez un Windows)

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo snap install docker

sudo apt install docker-compose

sudo apt-get install docker-compose-plugin

sudo docker compose -f docker-compose.prod.yml -d



3\)

L'appli est dispo, il suffit d'aller sur http://localhost/auth

(http://localhost/apidocs/#/ est aussi dispo)



4\)

Enfin pour arrêter le service, il suffit de faire

sudo docker compose -f docker-compose.prod.yml down







Composants / Architecture:



Frontend (React + Vite) :

&nbsp;   Application Single Page (SPA) rapide et réactive.

&nbsp;   Utilise `TailwindCSS` pour un design moderne et responsive.

&nbsp;   Communique avec l'API via des requêtes AJAX (Fetch/Axios).

Backend (Python Flask) :

&nbsp;   API RESTful exposant les ressources (Users, Lists, Movies).

&nbsp;   Sécurité via JWT (JSON Web Tokens) pour l'authentification sans état (stateless).

&nbsp;   ORM SQLAlchemy pour l'abstraction de la base de données.

&nbsp;   Serveur WSGI \*\*Gunicorn\*\* pour la performance en production.

Base de Données (MySQL) :

&nbsp;   Stockage relationnel robuste pour assurer l'intégrité des données (clés étrangères, cascades).

Gateway (Nginx) :

&nbsp;   Reverse Proxy unique qui route le trafic vers le Frontend (fichiers statiques) ou le Backend (API).

&nbsp;   Élimine les problèmes de CORS en production.









APIs externes :



Listes des API dans http://localhost/apidocs/#/ --> faciles d'utilisation



Exemples de Routes API



Inscription

POST http://localhost/api/auth/register?username=sel\&password=sel



Voir listes de l'user

GET http://localhost/api/lists/mine?username=sel\&password=sel



