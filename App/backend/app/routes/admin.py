from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User, List, Movie
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def is_admin():
    current_user_id = get_jwt_identity()
    return current_user_id == "admin"

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        users = User.query.filter(User.username != admin_username).all()
        result = []
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
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
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
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')
        
        if new_username:
            # Check for uniqueness
            existing = User.query.filter_by(username=new_username).first()
            if existing and existing.id != user.id:
                return jsonify({"msg": "Username already taken"}), 409
            user.username = new_username
            
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
    if not is_admin():
        return jsonify({"msg": "Unauthorized"}), 403
        
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"msg": "Movie not found"}), 404
        
    db.session.delete(movie)
    db.session.commit()
    
    return jsonify({"msg": "Movie deleted"}), 200
