from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import Movie, User
from flask_jwt_extended import jwt_required, get_jwt_identity

# Blueprint pour la gestion des films
bp = Blueprint('movies', __name__, url_prefix='/api/movies')

@bp.route('/search', methods=['GET'])
@jwt_required(optional=True)
def search():
    """
    Recherche des films dans la base de données locale (et potentiellement externe TMDB).
    Supporte le filtrage par année.
    ---
    tags:
      - Movies
    parameters:
      - name: username
        in: query
        type: string
        description: Authentification optionnelle
      - name: password
        in: query
        type: string
        description: Authentification optionnelle
      - name: query
        in: query
        type: string
        description: Titre du film à rechercher
      - name: year
        in: query
        type: string
        description: Année de sortie (filtre)
    responses:
      200:
        description: Résultats de la recherche
    """
    username = request.args.get('username')
    password = request.args.get('password')
    user_id = None
    
    # Authentification pour recherche (peut être restreinte aux utilisateurs connectés)
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            user_id = user.id
            
    if not user_id:
        user_id = get_jwt_identity()
        
    if not user_id:
        return jsonify({"msg": "Unauthorized - Provide valid credentials or token"}), 401
    
    query = request.args.get('query', '')
    year = request.args.get('year', '')
    
    query_obj = Movie.query

    # Filtre par titre (contient la chaine, insensible à la casse)
    if query:
        query_obj = query_obj.filter(Movie.title.ilike(f'%{query}%'))
    
    # Filtre par année (commence par l'année donnée)
    if year:
        query_obj = query_obj.filter(Movie.release_date.ilike(f'{year}%'))
    
    # Limite les résultats pour éviter de surcharger la réponse
    if not query and not year:
        local_results = query_obj.limit(20).all()
    else:
        local_results = query_obj.limit(10).all()
    
    results = []
    for movie in local_results:
        results.append({
            "id": movie.id,
            "title": movie.title,
            "poster_path": movie.poster_path,
            "release_date": movie.release_date,
            "is_custom": movie.is_custom
        })
        
    return jsonify({"results": results})

@bp.route('/', methods=['POST'])
@jwt_required(optional=True)
def create_custom_movie():
    """
    Crée un film personnalisé, utile quand le film n'est pas trouvé dans la base standard.
    ---
    tags:
      - Movies
    parameters:
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
      - name: title
        in: query
        type: string
        required: true
        description: Titre du film
      - name: release_date
        in: query
        type: string
        description: Date de sortie (YYYY-MM-DD ou YYYY)
    responses:
      201:
        description: Film créé
    """
    username = request.args.get('username')
    password = request.args.get('password')
    user_id = None
    
    auth_success = False
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            auth_success = True
            
    if not auth_success:
        if get_jwt_identity():
            auth_success = True
            
    if not auth_success:
        return jsonify({"msg": "Unauthorized - Provide valid credentials or token"}), 401

    title = request.args.get('title')
    release_date = request.args.get('release_date')
    
    if not title:
        return jsonify({"msg": "Title is required"}), 400
        
    # Vérifie si le film existe déjà pour éviter les doublons
    existing = Movie.query.filter(Movie.title.ilike(title)).first()
    if existing:
        return jsonify({
            "id": existing.id,
            "title": existing.title,
            "poster_path": existing.poster_path,
            "release_date": existing.release_date
        }), 200
        
    # Création du nouveau film
    new_movie = Movie(title=title, poster_path=None, release_date=release_date)
    db.session.add(new_movie)
    db.session.commit()
    
    return jsonify({
        "id": new_movie.id,
        "title": new_movie.title,
        "poster_path": new_movie.poster_path,
        "release_date": new_movie.release_date,
        "is_custom": True
    }), 201

def seed_movies():
    """
    Fonction utilitaire pour peupler la base de données avec des films initiaux "classiques".
    Exécutée au démarrage de l'application via update_movies.py ou app/__init__.py.
    """
    initial_movies = [
        {"title": "Inception", "poster_path": "/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg", "release_date": "2010-07-15"},
        {"title": "The Dark Knight", "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "release_date": "2008-07-16"},
        {"title": "Interstellar", "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "release_date": "2014-11-05"},
        {"title": "Pulp Fiction", "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "release_date": "1994-09-10"},
        {"title": "Fight Club", "poster_path": "https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_poster.jpg", "release_date": "1999-10-15"},
        {"title": "Forrest Gump", "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "release_date": "1994-07-06"},
        {"title": "The Matrix", "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "release_date": "1999-03-31"},
        {"title": "Le Seigneur des Anneaux : Le Retour du Roi", "poster_path": "/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg", "release_date": "2003-12-01"},
        {"title": "La La Land", "poster_path": "https://upload.wikimedia.org/wikipedia/en/a/ab/La_La_Land_%29film%29.png", "release_date": "2016-12-09"},
        {"title": "Avengers: Endgame", "poster_path": "/or06FN3Dka5tukK1e9sl16pB3iy.jpg", "release_date": "2019-04-24"}
    ]
    
    updated_count = 0
    added_count = 0
    
    for m in initial_movies:
        existing = Movie.query.filter(Movie.title.ilike(m['title'])).first()
        if existing:
            # Mise à jour des infos si elles ont changé
            if existing.poster_path != m['poster_path'] or existing.release_date != m['release_date']:
                existing.poster_path = m['poster_path']
                existing.release_date = m['release_date']
                updated_count += 1
        else:
            # Ajout du nouveau film
            db.session.add(Movie(title=m['title'], poster_path=m['poster_path'], release_date=m['release_date'], is_custom=False))
            added_count += 1
    
    try:
        if updated_count > 0 or added_count > 0:
            db.session.commit()
            print(f"Database seeded! ({added_count} added, {updated_count} updated)")
        else:
            # Assurance que les films par défaut ne sont pas marqués comme custom
            for m in initial_movies:
                mov = Movie.query.filter_by(title=m['title']).first()
                if mov and mov.is_custom:
                    mov.is_custom = False
                    db.session.add(mov)
            db.session.commit()
            
            print("Database already up to date.")
    except Exception as e:
        print(f"Error seeding: {e}")
        db.session.rollback()
