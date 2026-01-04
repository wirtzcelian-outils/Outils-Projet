from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
import sys
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Register attempt for: {data.get('username')}", file=sys.stderr)
        
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "Username already exists"}), 409

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
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')

        if admin_username and admin_password and username == admin_username and password == admin_password:
             access_token = create_access_token(identity="admin")
             return jsonify({
                 "access_token": access_token,
                 "user": {
                     "id": "admin",
                     "username": "admin",
                     "role": "admin"
                 }
             }), 200

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
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
