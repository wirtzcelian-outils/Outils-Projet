from flask import Blueprint, request, jsonify
from app import db
from app.models import List, ListItem, Movie
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

bp = Blueprint('lists', __name__, url_prefix='/api/lists')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_list():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name', 'Ma Liste')
    
    new_list = List(user_id=user_id, name=name)
    db.session.add(new_list)
    db.session.commit()
    
    return jsonify({
        "id": new_list.id,
        "name": new_list.name,
        "public_id": new_list.public_id,
        "private_id": new_list.private_id
    }), 201

@bp.route('/<string:list_id_str>', methods=['GET'])
def get_list(list_id_str):
    # Try public ID first
    movie_list = List.query.filter_by(public_id=list_id_str).first()
    is_owner = False
    
    if not movie_list:
        # Try private ID
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
        "is_owner": is_owner,
        "public_id": movie_list.public_id,
        "private_id": movie_list.private_id if is_owner else None,
        "items": items
    })

@bp.route('/<string:private_id>/items', methods=['POST'])
def add_item(private_id):
    # No JWT required for editing via private link (as per requirements/implicit auth via secret link)
    # However, for security, we could enforce it. Let's stick to the prompt's "private identifier to modify".
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    data = request.get_json()
    movie_id = data.get('movie_id')
    title = data.get('title')
    poster_path = data.get('poster_path')
    
    if not movie_id:
        return jsonify({"msg": "Movie ID required"}), 400
        
    # Check if movie exists in DB, else create
    movie = Movie.query.get(movie_id)
    if not movie:
        movie = Movie(id=movie_id, title=title, poster_path=poster_path)
        db.session.add(movie)
    
    # Calculate rank (append)
    max_rank = db.session.query(db.func.max(ListItem.rank)).filter_by(list_id=movie_list.id).scalar() or 0
    
    new_item = ListItem(list_id=movie_list.id, movie_id=movie_id, rank=max_rank + 1)
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({"msg": "Movie added"}), 201

@bp.route('/<string:private_id>/reorder', methods=['PUT'])
def reorder_items(private_id):
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    data = request.get_json()
    items_order = data.get('items') # List of {id: item_id, rank: new_rank}
    
    if not items_order:
        return jsonify({"msg": "Items order required"}), 400
        
    for item_data in items_order:
        item = ListItem.query.get(item_data['id'])
        if item and item.list_id == movie_list.id:
            item.rank = item_data['rank']
            
    db.session.commit()
    return jsonify({"msg": "List reordered"}), 200

@bp.route('/mine', methods=['GET'])
@jwt_required()
def get_my_lists():
    user_id = get_jwt_identity()
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
    movie_list = List.query.filter_by(private_id=private_id).first()
    if not movie_list:
        return jsonify({"msg": "List not found"}), 404
        
    db.session.delete(movie_list)
    db.session.commit()
    
    return jsonify({"msg": "List deleted"}), 200
