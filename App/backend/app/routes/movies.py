from flask import Blueprint, request, jsonify
from app import db
from app.models import Movie
from flask_jwt_extended import jwt_required

bp = Blueprint('movies', __name__, url_prefix='/api/movies')

@bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    query = request.args.get('query', '')
    year = request.args.get('year', '')
    
    query_obj = Movie.query

    if query:
        query_obj = query_obj.filter(Movie.title.ilike(f'%{query}%'))
    
    if year:
        query_obj = query_obj.filter(Movie.release_date.ilike(f'%{year}%'))
    
    if not query and not year:
        # Default library view
        movies = query_obj.limit(20).all()
    else:
        movies = query_obj.all()
    
    results = []
    for m in movies:
        results.append({
            "id": m.id,
            "title": m.title,
            "poster_path": m.poster_path, # Can be full URL or None
            "release_date": m.release_date or "N/A"
        })
        
    return jsonify({"results": results})

@bp.route('/', methods=['POST'])
@jwt_required()
def create_custom_movie():
    data = request.get_json()
    title = data.get('title')
    release_date = data.get('release_date')
    
    if not title:
        return jsonify({"msg": "Title is required"}), 400
        
    # Check if exists
    existing = Movie.query.filter(Movie.title.ilike(title)).first()
    if existing:
        return jsonify({
            "id": existing.id,
            "title": existing.title,
            "id": existing.id,
            "title": existing.title,
            "poster_path": existing.poster_path,
            "release_date": existing.release_date
        }), 200
        
    new_movie = Movie(title=title, poster_path=None, release_date=release_date) # No poster for custom movies by default
    db.session.add(new_movie)
    db.session.commit()
    
    return jsonify({
        "id": new_movie.id,
        "title": new_movie.title,
        "poster_path": new_movie.poster_path,
        "release_date": new_movie.release_date,
        "is_custom": True
    }), 201

# Seeder helper (called from app factory)
def seed_movies():
    initial_movies = [
        {"title": "Inception", "poster_path": "/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg", "release_date": "2010-07-15"},
        {"title": "The Dark Knight", "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "release_date": "2008-07-16"},
        {"title": "Interstellar", "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "release_date": "2014-11-05"},
        {"title": "Pulp Fiction", "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "release_date": "1994-09-10"},
        {"title": "Fight Club", "poster_path": "https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_poster.jpg", "release_date": "1999-10-15"},
        {"title": "Forrest Gump", "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "release_date": "1994-07-06"},
        {"title": "The Matrix", "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "release_date": "1999-03-31"},
        {"title": "Le Seigneur des Anneaux : Le Retour du Roi", "poster_path": "/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg", "release_date": "2003-12-01"},
        {"title": "La La Land", "poster_path": "https://upload.wikimedia.org/wikipedia/en/a/ab/La_La_Land_%28film%29.png", "release_date": "2016-12-09"},
        {"title": "Avengers: Endgame", "poster_path": "/or06FN3Dka5tukK1e9sl16pB3iy.jpg", "release_date": "2019-04-24"}
    ]
    
    updated_count = 0
    added_count = 0
    
    for m in initial_movies:
        # Check if movie exists (by title)
        existing = Movie.query.filter(Movie.title.ilike(m['title'])).first()
        if existing:
            # Update poster/date if changed
            if existing.poster_path != m['poster_path'] or existing.release_date != m['release_date']:
                existing.poster_path = m['poster_path']
                existing.release_date = m['release_date']
                updated_count += 1
        else:
            db.session.add(Movie(title=m['title'], poster_path=m['poster_path'], release_date=m['release_date'], is_custom=False))
            added_count += 1
    
    try:
        if updated_count > 0 or added_count > 0:
            db.session.commit()
            print(f"Database seeded! ({added_count} added, {updated_count} updated)")
        else:
            # OPTIONAL: Ensure existing seeded movies are flagged as not custom
            # This is slow but safer for migration. Or we just trust the new column default=True vs manual update.
            # Let's run a quick bulk update for safety if needed, OR just leave it.
            # The migration script to add column will default to True usually if we don't specify, 
            # or NULL. We defined default=True in model.
            # Let's force update these generic titles to False.
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
