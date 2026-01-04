import sys
import os
sys.path.append(os.getcwd())
from app import create_app
from app.routes.movies import seed_movies

app = create_app()
with app.app_context():
    seed_movies()
