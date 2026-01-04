from flask import Blueprint, request, jsonify
from app import db
from app.models import Movie
from flask_jwt_extended import jwt_required

bp = Blueprint('movies', __name__, url_prefix='/api/movies')

@bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    query = request.args.get('query', '')
    
    if not query:
        # Return random or top movies if no query
        movies = Movie.query.limit(20).all()
    else:
        # Local search
        movies = Movie.query.filter(Movie.title.ilike(f'%{query}%')).all()
    
    results = []
    for m in movies:
        results.append({
            "id": m.id,
            "title": m.title,
            "poster_path": m.poster_path, # Can be full URL or None
            "release_date": "2023" # Dummy default if not stored
        })
        
    return jsonify({"results": results})

@bp.route('/', methods=['POST'])
@jwt_required()
def create_custom_movie():
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({"msg": "Title is required"}), 400
        
    # Check if exists
    existing = Movie.query.filter(Movie.title.ilike(title)).first()
    if existing:
        return jsonify({
            "id": existing.id,
            "title": existing.title,
            "poster_path": existing.poster_path
        }), 200
        
    new_movie = Movie(title=title, poster_path=None) # No poster for custom movies by default
    db.session.add(new_movie)
    db.session.commit()
    
    return jsonify({
        "id": new_movie.id,
        "title": new_movie.title,
        "poster_path": new_movie.poster_path
    }), 201

# Seeder helper (called from app factory)
def seed_movies():
    initial_movies = [
        {"title": "Inception", "poster_path": "/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg"},
        {"title": "The Dark Knight", "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg"},
        {"title": "Interstellar", "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"},
        {"title": "Pulp Fiction", "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"},
        {"title": "Fight Club", "poster_path": "https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_poster.jpg"},
        {"title": "Forrest Gump", "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"},
        {"title": "The Matrix", "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"},
        {"title": "Le Seigneur des Anneaux : Le Retour du Roi", "poster_path": "/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg"},
        {"title": "La La Land", "poster_path": "https://upload.wikimedia.org/wikipedia/en/a/ab/La_La_Land_%28film%29.png"},
        {"title": "Avengers: Endgame", "poster_path": "/or06FN3Dka5tukK1e9sl16pB3iy.jpg"}
    ]
    
    updated_count = 0
    added_count = 0
    
    for m in initial_movies:
        # Check if movie exists (by title)
        existing = Movie.query.filter(Movie.title.ilike(m['title'])).first()
        if existing:
            # Update poster if changed
            if existing.poster_path != m['poster_path']:
                existing.poster_path = m['poster_path']
                updated_count += 1
        else:
            db.session.add(Movie(title=m['title'], poster_path=m['poster_path']))
            added_count += 1
    
    try:
        if updated_count > 0 or added_count > 0:
            db.session.commit()
            print(f"Database seeded! ({added_count} added, {updated_count} updated)")
        else:
            print("Database already up to date.")
    except Exception as e:
        print(f"Error seeding: {e}")
        db.session.rollback()
