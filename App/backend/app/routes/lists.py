from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User, List, ListItem, Movie
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

# Blueprint pour la gestion des listes de films
bp = Blueprint('lists', __name__, url_prefix='/api/lists')

@bp.route('/', methods=['POST'])
@jwt_required(optional=True)
def create_list():
    """
    Crée une nouvelle liste pour un utilisateur (authentifié par Token ou Identifiants directs).
    ---
    tags:
      - Lists
    parameters:
      - name: username
        in: query
        type: string
        required: true
        description: Nom d'utilisateur (si auth directe)
      - name: password
        in: query
        type: string
        required: true
        description: Mot de passe (si auth directe)
      - name: name
        in: query
        type: string
        description: Nom de la liste (par défaut "Ma Liste")
    responses:
      201:
        description: Liste créée
      401:
        description: Non autorisé
    """
    name = request.args.get('name', 'Ma Liste')
    
    # Tentative de récupération des identifiants dans les paramètres (pour les scripts/curl)
    username = request.args.get('username')
    password = request.args.get('password')
    user_id = None
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            user_id = user.id
            
    # Si pas d'identifiants directs, on tente le Token JWT
    if not user_id:
        user_id = get_jwt_identity()
        
    if not user_id:
        return jsonify({"msg": "Unauthorized - Provide valid credentials or token"}), 401
    
    new_list = List(user_id=user_id, name=name)
    db.session.add(new_list)
    db.session.commit()
    
    return jsonify({
        "id": new_list.id,
        "name": new_list.name,
        "public_id": new_list.public_id,
        "private_id": new_list.private_id
    }), 201

@bp.route('/lookup', methods=['GET'])
def lookup_list():
    """
    Recherche une liste spécifique en fournissant le nom d'utilisateur, le mot de passe et le nom de la liste.
    Permet un accès "programme" simple pour récupérer une liste.
    ---
    tags:
      - Lists
    parameters:
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
      - name: list_name
        in: query
        type: string
        required: true
    responses:
      200:
        description: Détails de la liste trouvée
    """
    username = request.args.get('username')
    password = request.args.get('password')
    list_name = request.args.get('list_name')
    
    if not username or not list_name or not password:
        return jsonify({"msg": "Username, password and list_name required"}), 400
        
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid password"}), 401
        
    movie_list = List.query.filter(
        List.user_id == user.id,
        List.name == list_name
    ).first()
    
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    # Construction de la liste des items
    items = []
    for item in movie_list.items:
        items.append({
            "id": item.id,
            "movie": {
                "id": item.movie.id,
                "title": item.movie.title,
                "poster_path": item.movie.poster_path
            },
            "rank": item.rank,
            "comment": item.comment
        })
        
    return jsonify({
        "id": movie_list.id,
        "name": movie_list.name,
        "owner_id": movie_list.user_id,
        "is_owner": True,
        "public_id": movie_list.public_id,
        "private_id": movie_list.private_id,
        "items": items
    })

@bp.route('/<string:list_id_str>', methods=['GET'])
def get_list(list_id_str):
    """
    Récupère une liste via son ID public ou privé.
    Si l'ID privé est utilisé, on considère que c'est le propriétaire qui accède (is_owner=True).
    """
    # Essai avec ID Public (Lecture seule par défaut)
    movie_list = List.query.filter_by(public_id=list_id_str).first()
    is_owner = False
    
    # Si non trouvé, essai avec ID Privé (Propriétaire)
    if not movie_list:
        movie_list = List.query.filter_by(private_id=list_id_str).first()
        if movie_list:
            is_owner = True
    
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    items = []
    for item in movie_list.items:
        items.append({
            "id": item.id,
            "movie": {
                "id": item.movie.id,
                "title": item.movie.title,
                "poster_path": item.movie.poster_path
            },
            "rank": item.rank,
            "comment": item.comment
        })
        
    return jsonify({
        "id": movie_list.id,
        "name": movie_list.name,
        "owner_id": movie_list.user_id,
        "is_owner": is_owner, # Indique au frontend si on a les droits d'édition
        "public_id": movie_list.public_id,
        "private_id": movie_list.private_id if is_owner else None, # On ne révèle l'ID privé qu'au propriétaire
        "items": items
    })

@bp.route('/<string:private_id>/items', methods=['POST'])
def add_item(private_id):
    """
    Ajoute un film à une liste (via ID privé pour autorisation).
    Si le film n'existe pas encore dans la DB, il est créé.
    """
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    data = request.get_json()
    movie_id = data.get('movie_id')
    title = data.get('title')
    poster_path = data.get('poster_path')
    
    if not movie_id:
        return jsonify({"msg": "Movie ID required"}), 400
        
    # Vérifie si le film existe, sinon le crée
    movie = Movie.query.get(movie_id)
    if not movie:
        movie = Movie(id=movie_id, title=title, poster_path=poster_path)
        db.session.add(movie)
    
    # Calcul du rang pour ajouter à la fin de la liste
    max_rank = db.session.query(db.func.max(ListItem.rank)).filter_by(list_id=movie_list.id).scalar() or 0
    
    new_item = ListItem(list_id=movie_list.id, movie_id=movie_id, rank=max_rank + 1)
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({"msg": "Movie added"}), 201

@bp.route('/<string:private_id>/reorder', methods=['PUT'])
def reorder_items(private_id):
    """
    Réordonne les éléments d'une liste.
    Reçoit une liste d'objets {id, rank} et met à jour la base.
    """
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    data = request.get_json()
    items_order = data.get('items')
    
    if not items_order:
        return jsonify({"msg": "Items order required"}), 400
        
    for item_data in items_order:
        item = ListItem.query.get(item_data['id'])
        # Sécurité : on vérifie que l'item appartient bien à la liste modifiée
        if item and item.list_id == movie_list.id:
            item.rank = item_data['rank']
            
    db.session.commit()
    return jsonify({"msg": "List reordered"}), 200

@bp.route('/mine', methods=['GET'])
@jwt_required(optional=True)
def get_my_lists():
    """
    Récupère toutes les listes de l'utilisateur connecté.
    ---
    tags:
      - Lists
    parameters:
      - name: username
        in: query
        type: string
        description: (auth directe)
      - name: password
        in: query
        type: string
        description: (auth directe)
    """
    username = request.args.get('username')
    password = request.args.get('password')
    user_id = None
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            user_id = user.id
            
    if not user_id:
        user_id = get_jwt_identity()
        
    if not user_id:
        return jsonify({"msg": "Unauthorized - Provide valid credentials or token"}), 401

    user_lists = List.query.filter_by(user_id=user_id).all()
    results = []
    for l in user_lists:
        results.append({
            "id": l.id,
            "name": l.name,
            "private_id": l.private_id,
            "public_id": l.public_id,
            "item_count": len(l.items)
        })
    return jsonify(results)

@bp.route('/<string:private_id>/items/<int:item_id>', methods=['DELETE'])
def remove_item(private_id, item_id):
    """
    Retire un film d'une liste (via ID privé).
    """
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    item = ListItem.query.get(item_id)
    if not item or item.list_id != movie_list.id:
        return jsonify({"msg": "Item not found in this list"}), 404
        
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({"msg": "Item removed"}), 200

@bp.route('/<string:private_id>/items/<int:item_id>', methods=['PUT'])
def update_item(private_id, item_id):
    """
    Met à jour un élément de liste (ex: modifier le commentaire).
    """
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    item = ListItem.query.get(item_id)
    if not item or item.list_id != movie_list.id:
        return jsonify({"msg": "Item not found in this list"}), 404
    
    data = request.get_json()
    if 'comment' in data:
        item.comment = data['comment']
        
    db.session.commit()
    
    return jsonify({
        "msg": "Item updated",
        "item": {
            "id": item.id,
            "comment": item.comment
        }
    }), 200

@bp.route('/<string:private_id>', methods=['PUT'])
def update_list(private_id):
    """
    Met à jour les métadonnées de la liste (ex: changer le nom).
    """
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
    
    data = request.get_json()
    if 'name' in data:
        movie_list.name = data['name']
        
    db.session.commit()
    
    return jsonify({
        "msg": "List updated",
        "list": {
            "id": movie_list.id,
            "name": movie_list.name
        }
    }), 200

@bp.route('/<string:private_id>', methods=['DELETE'])
def delete_list(private_id):
    """
    Supprime complètement une liste.
    """
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    db.session.delete(movie_list)
    db.session.commit()
    
    return jsonify({"msg": "List deleted"}), 200

@bp.route('/name/<string:list_name>/movies', methods=['POST'])
@jwt_required(optional=True)
def add_movie_by_names(list_name):
    """
    Ajoute un film à une liste en utilisant uniquement des NOMS (Nom de liste, Titre de film).
    Pratique pour l'automatisation.
    ---
    tags:
      - Lists
    parameters:
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
      - name: movie_title
        in: query
        type: string
        required: true
        description: Titre exact du film à ajouter
      - name: list_name
        in: path
        type: string
        required: true
    responses:
      201:
        description: Film ajouté
    """
    username = request.args.get('username')
    password = request.args.get('password')
    user_id = None
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            user_id = user.id
            
    if not user_id:
        user_id = get_jwt_identity()
        
    if not user_id:
        return jsonify({"msg": "Unauthorized"}), 401

    # Trouve la liste de l'utilisateur par son nom
    movie_list = List.query.filter_by(user_id=user_id, name=list_name).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404

    movie_title = request.args.get('movie_title')
    if not movie_title:
        return jsonify({"msg": "movie_title required"}), 400
        
    # Trouve le film par son titre (insensible à la casse)
    movie = Movie.query.filter(Movie.title.ilike(movie_title)).first()
    if not movie:
        return jsonify({"msg": "Movie not found"}), 404

    # Vérification doublon
    existing_item = ListItem.query.filter_by(list_id=movie_list.id, movie_id=movie.id).first()
    if existing_item:
        return jsonify({"msg": "Movie already in list"}), 200

    max_rank = db.session.query(db.func.max(ListItem.rank)).filter_by(list_id=movie_list.id).scalar() or 0
    
    new_item = ListItem(list_id=movie_list.id, movie_id=movie.id, rank=max_rank + 1)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"msg": "Movie added to list"}), 201

@bp.route('/name/<string:list_name>', methods=['DELETE'])
@jwt_required(optional=True)
def delete_list_by_name(list_name):
    """
    Supprime une liste en utilisant son nom.
    ---
    tags:
      - Lists
    parameters:
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
      - name: list_name
        in: path
        type: string
        required: true
    """
    username = request.args.get('username')
    password = request.args.get('password')
    user_id = None
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            user_id = user.id
            
    if not user_id:
        user_id = get_jwt_identity()
        
    if not user_id:
        return jsonify({"msg": "Unauthorized"}), 401

    movie_list = List.query.filter_by(user_id=user_id, name=list_name).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    db.session.delete(movie_list)
    db.session.commit()
    
    return jsonify({"msg": f"List '{list_name}' deleted"}), 200
