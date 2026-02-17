import pytest
from app import create_app, db
from app.config import TestConfig
from app.models import User

# Configuration des fixtures pour pytest
# Ces fonctions sont exécutées avant/après les tests pour préparer l'environnement

@pytest.fixture
def app():
    """
    Crée une instance de l'application Flask configurée pour les tests.
    Utilise une base de données SQLite en mémoire pour la rapidité et l'isolation.
    """
    # Configuration spécifique pour le test via TestConfig
    app = create_app(TestConfig)

    # Création des tables dans la base de données en mémoire
    with app.app_context():
        db.create_all()
        yield app
        # Nettoyage après les tests
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    Fournit un client de test qui simule un navigateur.
    Permet d'envoyer des requêtes HTTP (GET, POST, etc.) à l'application.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    Fournit un runner pour tester les commandes CLI de l'application (si besoin).
    """
    return app.test_cli_runner()

@pytest.fixture
def auth_token(client):
    """
    Helper pour créer un utilisateur, le connecter et récupérer un token JWT valide.
    Utile pour tester les routes protégées.
    """
    # 1. Création de l'utilisateur
    username = "testuser"
    password = "password123"
    client.post(f'/api/auth/register?username={username}&password={password}')
    
    # 2. Connexion pour avoir le token
    response = client.post(f'/api/auth/login?username={username}&password={password}')
    token = response.json['access_token']
    
    return token
