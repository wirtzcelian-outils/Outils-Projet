from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, UserProfile

# Blueprint pour la gestion du profil utilisateur
bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Récupère les informations de profil (Bio) de l'utilisateur connecté.
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    responses:
      200:
        description: Profil utilisateur (bio)
      404:
        description: Utilisateur non trouvé
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    if not user.profile:
        return jsonify({"bio": ""}), 200
        
    return jsonify({"bio": user.profile.bio}), 200

@bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Met à jour la bio de l'utilisateur connecté.
    Si le profil n'existe pas encore, il est créé.
    ---
    tags:
      - Profile
    parameters:
      - name: bio
        in: query
        type: string
        description: Nouveau contenu de la bio
    security:
      - Bearer: []
    responses:
      200:
        description: Profil mis à jour
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    bio_content = request.args.get('bio')
    
    if bio_content is None:
         return jsonify({"msg": "Bio parameter missing"}), 400

    if not user.profile:
        # Création du profil s'il n'existe pas
        new_profile = UserProfile(user_id=user.id, bio=bio_content)
        db.session.add(new_profile)
    else:
        # Mise à jour de la bio existante
        user.profile.bio = bio_content
        
    db.session.commit()
    
    return jsonify({"msg": "Bio updated", "bio": bio_content}), 200
