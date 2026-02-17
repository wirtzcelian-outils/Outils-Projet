import sys
import os

# Ajout du répertoire courant au chemin système pour permettre les imports relatifs
sys.path.append(os.getcwd())

from app import create_app
from app.routes.movies import seed_movies

# Création d'une instance de l'application pour avoir accès au contexte (base de données, etc.)
app = create_app()

# Utilisation du contexte de l'application pour exécuter des commandes liées à la DB
with app.app_context():
    # Lancement de la fonction de peuplement de la base de données de films
    seed_movies()
