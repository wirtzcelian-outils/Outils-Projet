import pytest
import os

# Tests unitaires pour l'Administration

def test_admin_route_protection(client, auth_token):
    """
    Sécurité : Vérifie qu'un utilisateur normal NE PEUT PAS accéder aux routes admin.
    """
    headers = {'Authorization': f'Bearer {auth_token}'} # Token d'un utilisateur normal
    
    response = client.get('/api/admin/users', headers=headers)
    
    assert response.status_code == 403 # Forbidden
    assert response.json['msg'] == "Unauthorized"

def test_admin_access_allowed(client):
    """
    Vérifie que l'admin (identifié par son ID spécial) peut accéder.
    Ceci nécessite de mocker ou d'utiliser le login admin.
    """
    # Configuration des variables d'env pour le test (simulé)
    os.environ['ADMIN_USERNAME'] = 'admin'
    os.environ['ADMIN_PASSWORD'] = 'adminpass'
    
    # 1. Login Admin
    login_res = client.post('/api/auth/login?username=admin&password=adminpass')
    assert login_res.status_code == 200
    admin_token = login_res.json['access_token']
    
    # 2. Accès route protégée
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/admin/users', headers=headers)
    
    assert response.status_code == 200
    # On doit recevoir une liste (vide ou non)
    assert isinstance(response.json, list)

def test_admin_delete_user(client):
    """
    Vérifie qu'un admin peut supprimer un utilisateur.
    """
    os.environ['ADMIN_USERNAME'] = 'admin'
    os.environ['ADMIN_PASSWORD'] = 'adminpass'
    
    # Création d'un user à supprimer
    client.post('/api/auth/register?username=todelete&password=pwd')
    
    # Connexion Admin
    login_res = client.post('/api/auth/login?username=admin&password=adminpass')
    admin_token = login_res.json['access_token']
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Récupérer l'ID de l'user créé (via la liste des users)
    users_res = client.get('/api/admin/users', headers=headers)
    target_user_id = users_res.json[0]['id']
    
    # Suppression
    del_res = client.delete(f'/api/admin/users/{target_user_id}', headers=headers)
    assert del_res.status_code == 200
    assert del_res.json['msg'] == "User deleted"
    
    # Vérification suppression
    users_res_after = client.get('/api/admin/users', headers=headers)
    assert len(users_res_after.json) == 0
