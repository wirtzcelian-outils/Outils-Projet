import pytest
from app.models import User

# Tests unitaires pour l'Authentification (Inscription et Connexion)

def test_register_user(client):
    """
    Vérifie qu'un nouvel utilisateur peut s'inscrire correctement.
    """
    username = "newuser"
    password = "password123"
    
    # Envoi de la requête d'inscription
    response = client.post(f'/api/auth/register?username={username}&password={password}')
    
    # Vérifications
    assert response.status_code == 201
    assert response.json['msg'] == "User created successfully"

def test_register_duplicate_user(client):
    """
    Vérifie que l'inscription échoue si le pseudo existe déjà.
    """
    # 1. Inscription initiale
    client.post('/api/auth/register?username=dupuser&password=password123')
    
    # 2. Tentative de réinscription avec le même pseudo
    response = client.post('/api/auth/register?username=dupuser&password=newpassword')
    
    assert response.status_code == 409
    assert response.json['msg'] == "Username already exists"

def test_login_success(client):
    """
    Vérifie que la connexion avec les bons identifiants renvoie un Token JWT.
    """
    # Préparation
    client.post('/api/auth/register?username=loginuser&password=password123')
    
    # Connexion
    response = client.post('/api/auth/login?username=loginuser&password=password123')
    
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json['user']['username'] == "loginuser"

def test_login_invalid(client):
    """
    Vérifie que la connexion échoue avec un mauvais mot de passe.
    """
    # Préparation
    client.post('/api/auth/register?username=wrongpass&password=password123')
    
    # Connexion mot de passe incorrect
    response = client.post('/api/auth/login?username=wrongpass&password=BADPASSWORD')
    
    assert response.status_code == 401
    assert response.json['msg'] == "Bad username or password"
