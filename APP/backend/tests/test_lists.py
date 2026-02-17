import pytest

# Tests unitaires pour la gestion des Listes

def test_create_list(client, auth_token):
    """
    Vérifie la création d'une liste pour un utilisateur connecté.
    """
    headers = {'Authorization': f'Bearer {auth_token}'}
    list_name = "Ma Liste Test"
    
    # Création
    response = client.post(f'/api/lists/?name={list_name}', headers=headers)
    
    assert response.status_code == 201
    assert response.json['name'] == list_name
    assert "public_id" in response.json
    assert "private_id" in response.json # Le créateur reçoit l'ID privé

def test_get_my_lists(client, auth_token):
    """
    Vérifie que l'utilisateur peut récupérer ses propres listes.
    """
    headers = {'Authorization': f'Bearer {auth_token}'}
    client.post('/api/lists/?name=Liste1', headers=headers)
    client.post('/api/lists/?name=Liste2', headers=headers)
    
    response = client.get('/api/lists/mine', headers=headers)
    
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['name'] == "Liste1"

def test_add_movie_to_list(client, auth_token):
    """
    Vérifie l'ajout d'un film à une liste et sa sauvegarde.
    """
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # 1. Créer une liste
    list_res = client.post('/api/lists/?name=Cinema', headers=headers)
    private_id = list_res.json['private_id']
    
    # 2. Créer un film (pour l'avoir en DB, même si add_item le crée aussi)
    # On simule un film TMDB
    movie_data = {
        "movie_id": 999,
        "title": "Film Test",
        "poster_path": "/path.jpg"
    }
    
    # 3. Ajouter le film
    add_res = client.post(f'/api/lists/{private_id}/items', json=movie_data, headers=headers)
    assert add_res.status_code == 201
    
    # 4. Vérifier qu'il est dans la liste
    get_res = client.get(f'/api/lists/{private_id}', headers=headers)
    items = get_res.json['items']
    assert len(items) == 1
    assert items[0]['movie']['title'] == "Film Test"

def test_delete_list(client, auth_token):
    """
    Vérifie la suppression d'une liste.
    """
    headers = {'Authorization': f'Bearer {auth_token}'}
    list_res = client.post('/api/lists/?name=ToDelete', headers=headers)
    private_id = list_res.json['private_id']
    
    # Suppression
    del_res = client.delete(f'/api/lists/{private_id}', headers=headers)
    assert del_res.status_code == 200
    
    # Vérification (doit être 404)
    get_res = client.get(f'/api/lists/{private_id}', headers=headers)
    assert get_res.status_code == 404
