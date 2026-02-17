from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db, bcrypt
from app.models import User, List, Movie, ListItem
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Création d'un Blueprint pour regrouper les routes d'administration
# Toutes les routes commenceront par /api/admin
bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def is_admin():
    """
    Vérifie si l'utilisateur connecté via JWT a le rôle d'administrateur.
    Dans cette implémentation simple, l'ID de l'admin est "admin".
    """
    current_user_id = get_jwt_identity()
    return current_user_id == "admin"

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """
    Récupère la liste de tous les utilisateurs (sauf l'admin lui-même).
    Renvoie aussi le nombre de listes créées par chaque utilisateur.
    """
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        # Récupération du nom d'utilisateur admin depuis les variables d'env pour l'exclure
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        users = User.query.filter(User.username != admin_username).all()
        result = []
        
        # Construction de la réponse JSON
        for user in users:
            list_count = List.query.filter_by(user_id=user.id).count()
            result.append({
                "id": user.id,
                "username": user.username,
                "list_count": list_count,
                "created_at": user.created_at.isoformat()
            })
        return jsonify(result), 200
    except Exception as e:
        print(f"Error fetching users: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Supprime un utilisateur spécifique par son ID.
    Accès réservé à l'administrateur.
    """
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        # La suppression de l'utilisateur supprimera en cascade ses listes et profils
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Modifie les informations d'un utilisateur (pseudo ou mot de passe).
    Accès réservé à l'administrateur.
    """
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')
        
        # Vérification de l'unicité du pseudo si modifié
        if new_username:
            existing = User.query.filter_by(username=new_username).first()
            if existing and existing.id != user.id:
                return jsonify({"msg": "Username already taken"}), 409
            user.username = new_username
            
        # Hachage du nouveau mot de passe si modifié
        if new_password:
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            
        db.session.commit()
        return jsonify({"msg": "User updated"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500

@bp.route('/movies/custom', methods=['GET'])
@jwt_required()
def get_custom_movies():
    """
    Récupère la liste des films ajoutés manuellement par les utilisateurs (is_custom=True).
    Ces films peuvent être supprimés par l'admin s'ils sont inappropriés.
    """
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
        
    movies = Movie.query.filter_by(is_custom=True).all()
    results = []
    for m in movies:
        results.append({
            "id": m.id,
            "title": m.title,
            "release_date": m.release_date or "N/A"
        })
    return jsonify(results)

@bp.route('/movies/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id):
    """
    Supprime un film de la base de données.
    Attention : supprimer un film le supprimera aussi de toutes les listes qui le contiennent (Cascade).
    """
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
        
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"msg": "Movie not found"}), 404
        
    db.session.delete(movie)
    db.session.commit()
    
    return jsonify({"msg": "Movie deleted"}), 200

@bp.route('/users/name/<string:target_username>', methods=['DELETE'])
@jwt_required(optional=True)
def delete_user_by_name(target_username):
    """
    Supprime un utilisateur en utilisant son pseudo.
    Supporte l'authentification par Token JWT OU par identifiants Admin passés en paramètres (utile pour les scripts).
    ---
    tags:
      - Admin
    parameters:
      - name: username
        in: query
        type: string
        required: true
        description: Nom d'utilisateur Admin (optionnel si Token présent)
      - name: password
        in: query
        type: string
        required: true
        description: Mot de passe Admin (optionnel si Token présent)
      - name: target_username
        in: path
        type: string
        required: true
        description: Pseudo de l'utilisateur à supprimer
    security:
      - Bearer: []
    responses:
      200:
        description: Utilisateur supprimé avec succès
      403:
        description: Non autorisé
      404:
        description: Utilisateur non trouvé
    """
    # Récupération des identifiants directs (query params)
    direct_user = request.args.get('username')
    direct_pass = request.args.get('password')
    
    admin_user_env = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_pass_env = os.environ.get('ADMIN_PASSWORD', 'admin')
    
    # Vérification de l'authentification directe
    is_direct_admin = False
    if direct_user and direct_pass:
        if direct_user == admin_user_env and direct_pass == admin_pass_env:
            is_direct_admin = True

    # Si ni authentifié directement ni par Token Admin -> Refus
    if not is_direct_admin and not is_admin():
        return jsonify({"msg": "Unauthorized - Admin access required"}), 403
    
    try:
        user = User.query.filter_by(username=target_username).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # Protection contre la suppression de l'admin lui-même
        if user.username == admin_user_env:
             return jsonify({"msg": "Cannot delete admin user"}), 400

        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": f"User {target_username} deleted"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500

@bp.route('/movies/title/<string:target_title>', methods=['DELETE'])
@jwt_required(optional=True)
def delete_movie_by_title(target_title):
    """
    Supprime un film personnalisé par son titre.
    Ne permet pas de supprimer les films système (ceux ajoutés par défaut).
    ---
    tags:
      - Admin
    parameters:
      - name: username
        in: query
        type: string
        required: true
        description: Admin username
      - name: password
        in: query
        type: string
        required: true
        description: Admin password
      - name: target_title
        in: path
        type: string
        required: true
        description: Titre du film à supprimer
    security:
      - Bearer: []
    responses:
      200:
        description: Film supprimé
      403:
        description: Interdit (Film système ou non admin)
      404:
        description: Film non trouvé
    """
    direct_user = request.args.get('username')
    direct_pass = request.args.get('password')
    
    admin_user_env = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_pass_env = os.environ.get('ADMIN_PASSWORD', 'admin')
    
    is_direct_admin = False
    if direct_user and direct_pass:
        if direct_user == admin_user_env and direct_pass == admin_pass_env:
            is_direct_admin = True

    if not is_direct_admin and not is_admin():
        return jsonify({"msg": "Unauthorized - Admin access required"}), 403

    try:
        # Recherche insensible à la casse (ilike)
        movie = Movie.query.filter(Movie.title.ilike(target_title)).first()
        if not movie:
             return jsonify({"msg": "Movie not found"}), 404
             
        # Sécurité : on ne supprime que les films custom
        if not movie.is_custom:
            return jsonify({"msg": "Forbidden - Cannot delete system movies"}), 403
            
        db.session.delete(movie)
        db.session.commit()
        
        return jsonify({"msg": f"Movie '{movie.title}' deleted"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting movie: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500

@bp.route('/export', methods=['GET'])
@jwt_required(optional=True)
def export_data():
    """
    Exporte toutes les données de la base (Utilisateurs, Films, Listes, Éléments de liste) au format JSON.
    Utile pour la sauvegarde ou la migration.
    ---
    tags:
      - Admin
    parameters:
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: Fichier JSON complet des données
    """
    username = request.args.get('username')
    password = request.args.get('password')
    
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    is_direct_admin = False
    if username and password and admin_username and admin_password:
        if username == admin_username and password == admin_password:
            is_direct_admin = True

    current_user = get_jwt_identity()
    if not is_direct_admin and current_user != "admin":
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        # --- Export des Utilisateurs ---
        users = User.query.all()
        users_data = []
        for u in users:
            users_data.append({
                "id": u.id,
                "username": u.username,
                "password_hash": u.password_hash, # Export du hash pour pouvoir restaurer à l'identique
                "created_at": u.created_at.isoformat()
            })

        # --- Export des Films ---
        movies = Movie.query.all()
        movies_data = []
        for m in movies:
            movies_data.append({
                "id": m.id,
                "title": m.title,
                "poster_path": m.poster_path,
                "release_date": m.release_date,
                "is_custom": m.is_custom
            })

        # --- Export des Listes ---
        lists = List.query.all()
        lists_data = []
        for l in lists:
            lists_data.append({
                "id": l.id,
                "user_id": l.user_id,
                "name": l.name,
                "public_id": l.public_id,
                "private_id": l.private_id,
                "is_public": l.is_public,
                "created_at": l.created_at.isoformat()
            })

        # --- Export des Éléments de Liste ---
        from app.models import ListItem
        list_items = ListItem.query.all()
        list_items_data = []
        for li in list_items:
            list_items_data.append({
                "id": li.id,
                "list_id": li.list_id,
                "movie_id": li.movie_id,
                "rank": li.rank,
                "comment": li.comment
            })

        # Construction de l'objet final
        export_data = {
            "users": users_data,
            "movies": movies_data,
            "lists": lists_data,
            "list_items": list_items_data,
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat()
        }

        return jsonify(export_data), 200

    except Exception as e:
        print(f"Error exporting data: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500

@bp.route('/import', methods=['POST'])
@jwt_required()
def import_data():
    """
    Importe les données depuis un fichier JSON.
    Gère les conflits en vérifiant si les éléments existent déjà.
    Reconstruit les relations via des dictionnaires de mapping (Ancien ID -> Nouvel ID).
    """
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        data = request.get_json()
        if not data:
             return jsonify({"msg": "No data provided"}), 400

        # Dictionnaires pour mapper les anciens IDs (du fichier import) vers les nouveaux IDs (base actuelle)
        user_map = {}
        movie_map = {}
        list_map = {}

        # --- Import des Utilisateurs ---
        users_data = data.get('users', [])
        for u_data in users_data:
            existing = User.query.filter_by(username=u_data['username']).first()
            if existing:
                user_map[u_data['id']] = existing.id # On garde l'ID existant
            else:
                new_user = User(
                    username=u_data['username'],
                    password_hash=u_data['password_hash'], 
                    created_at=datetime.fromisoformat(u_data['created_at']) if u_data.get('created_at') else datetime.utcnow()
                )
                db.session.add(new_user)
                db.session.flush() # Flush pour récupérer le nouvel ID généré
                user_map[u_data['id']] = new_user.id
        
        # --- Import des Films ---
        movies_data = data.get('movies', [])
        for m_data in movies_data:
            existing = Movie.query.filter(Movie.title.ilike(m_data['title'])).first()
            if existing:
                movie_map[m_data['id']] = existing.id
            else:
                new_movie = Movie(
                    title=m_data['title'],
                    poster_path=m_data.get('poster_path'),
                    release_date=m_data.get('release_date'),
                    is_custom=m_data.get('is_custom', True)
                )
                db.session.add(new_movie)
                db.session.flush()
                movie_map[m_data['id']] = new_movie.id

        # --- Import des Listes ---
        lists_data = data.get('lists', [])
        for l_data in lists_data:
            old_user_id = l_data['user_id']
            # Si le propriétaire n'a pas pu être importé/trouvé, on ignore la liste
            if old_user_id not in user_map:
                continue 

            new_owner_id = user_map[old_user_id]
            
            # On vérifie par public_id si la liste existe déjà
            existing = List.query.filter_by(public_id=l_data['public_id']).first()
            if existing:
                list_map[l_data['id']] = existing.id
            else:
                new_list = List(
                    user_id=new_owner_id,
                    name=l_data['name'],
                    public_id=l_data.get('public_id'),
                    private_id=l_data.get('private_id'),
                    is_public=l_data.get('is_public', True),
                    created_at=datetime.fromisoformat(l_data['created_at']) if l_data.get('created_at') else datetime.utcnow()
                )
                db.session.add(new_list)
                db.session.flush()
                list_map[l_data['id']] = new_list.id

        # --- Import des Éléments de Liste ---
        from app.models import ListItem
        list_items_data = data.get('list_items', [])
        for li_data in list_items_data:
            old_list_id = li_data['list_id']
            old_movie_id = li_data['movie_id']

            # Vérification que la liste et le film existent bien dans le nouveau contexte
            if old_list_id not in list_map or old_movie_id not in movie_map:
                continue
            
            new_list_id = list_map[old_list_id]
            new_movie_id = movie_map[old_movie_id]

            # On évite les doublons dans la liste
            existing_item = ListItem.query.filter_by(list_id=new_list_id, movie_id=new_movie_id).first()
            if not existing_item:
                new_item = ListItem(
                    list_id=new_list_id,
                    movie_id=new_movie_id,
                    rank=li_data.get('rank', 0),
                    comment=li_data.get('comment')
                )
                db.session.add(new_item)

        db.session.commit()
        return jsonify({"msg": "Import successful", "details": f"Processed {len(users_data)} users, {len(movies_data)} movies, {len(lists_data)} lists"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error importing data: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500
