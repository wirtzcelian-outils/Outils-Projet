from datetime import datetime
import uuid
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lists = db.relationship('List', backref='owner', lazy=True, cascade="all, delete-orphan")

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True) # TMDB ID
    title = db.Column(db.String(255), nullable=False)
    poster_path = db.Column(db.String(255))
    release_date = db.Column(db.String(20)) # Format YYYY-MM-DD or YYYY
    is_custom = db.Column(db.Boolean, default=True) # True=User Created, False=System/Seeded
    # We can cache more data here if needed

class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    public_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    private_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('ListItem', backref='list', lazy=True, cascade="all, delete-orphan", order_by='ListItem.rank')

class ListItem(db.Model):
    __tablename__ = 'list_items'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    rank = db.Column(db.Integer, nullable=False) # Order in the list
    comment = db.Column(db.Text)
    
    movie = db.relationship('Movie')
