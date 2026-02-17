from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
import sys
import os

# Blueprint pour l'authentification
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """
    Inscrit un nouvel utilisateur.
    Hashage du mot de passe avec Bcrypt avant stockage.
    ---
    tags:
      - Auth
    parameters:
      - name: username
        in: query
        type: string
        required: true
        description: Nom d'utilisateur souhaité
      - name: password
        in: query
        type: string
        required: true
        description: Mot de passe souhaité
    responses:
      201:
        description: Utilisateur créé avec succès
      400:
        description: Données manquantes
      409:
        description: Nom d'utilisateur déjà pris
    """
    try:
        print(f"Register attempt for: {request.args.get('username')}", file=sys.stderr)
        
        username = request.args.get('username')
        password = request.args.get('password')

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        # Vérification si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "Username already exists"}), 409

        # Hachage sécurisé du mot de passe
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        
        print(f"User {username} created successfully", file=sys.stderr)
        return jsonify({"msg": "User created successfully"}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    Authentifie un utilisateur et renvoie un Token JWT (headers) + infos utilisateur.
    Gère aussi l'authentification spéciale pour l'Admin système (variables d'env).
    ---
    tags:
      - Auth
    parameters:
      - name: username
        in: query
        type: string
        required: true
        description: Nom d'utilisateur
      - name: password
        in: query
        type: string
        required: true
        description: Mot de passe
    responses:
      200:
        description: Connexion réussie, renvoie le token
      401:
        description: Identifiants invalides
    """
    try:
        username = request.args.get('username')
        password = request.args.get('password')

        # Vérification des identifiants admin (configurés en variables d'environnement)
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')

        if admin_username and admin_password and username == admin_username and password == admin_password:
             # Création d'un token spécial pour l'admin
             access_token = create_access_token(identity="admin")
             return jsonify({
                 "access_token": access_token,
                 "user": {
                     "id": "admin",
                     "username": "admin",
                     "role": "admin"
                 }
             }), 200

        # Vérification dans la base de données pour les utilisateurs normaux
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Création du token d'accès avec l'ID utilisateur comme identité
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username
                }
            }), 200

        return jsonify({"msg": "Bad username or password"}), 401
    except Exception as e:
        print(f"Error during login: {str(e)}", file=sys.stderr)
        return jsonify({"msg": "Internal Server Error"}), 500
