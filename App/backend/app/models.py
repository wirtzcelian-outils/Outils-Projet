from datetime import datetime
import uuid
from . import db

class User(db.Model):
    """
    Modèle représentant un utilisateur de l'application.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation One-to-Many avec les listes de l'utilisateur
    # cascade="all, delete-orphan" assure que les listes sont supprimées si l'utilisateur l'est
    lists = db.relationship('List', backref='owner', lazy=True, cascade="all, delete-orphan")
    
    # Relation One-to-One avec le profil utilisateur (Bio)
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade="all, delete-orphan")

class UserProfile(db.Model):
    """
    Modèle pour les informations étendues du profil utilisateur (ex: Bio).
    """
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text)

class Movie(db.Model):
    """
    Modèle représentant un film (soit importé de TMDB, soit créé par un utilisateur).
    """
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    poster_path = db.Column(db.String(255)) # URL ou chemin de l'affiche
    release_date = db.Column(db.String(20)) # Date de sortie (souvent juste l'année)
    is_custom = db.Column(db.Boolean, default=True) # True si ajouté manuellement par un utilisateur

class List(db.Model):
    """
    Modèle représentant une liste de films créée par un utilisateur.
    """
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # IDs publics (lecture seule) et privés (édition) pour le partage
    public_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    private_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec les éléments de la liste (films ajoutés)
    items = db.relationship('ListItem', backref='list', lazy=True, cascade="all, delete-orphan", order_by='ListItem.rank')

class ListItem(db.Model):
    """
    Table de liaison entre une liste et un film.
    Stocke aussi le rang (ordre) et le commentaire personnel.
    """
    __tablename__ = 'list_items'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    
    # ondelete='CASCADE' assure que l'élément de liste est supprimé si le film est supprimé de la base globale
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    
    rank = db.Column(db.Integer, nullable=False) # Ordre dans la liste
    comment = db.Column(db.Text) # Commentaire optionnel de l'utilisateur sur ce film
    
    movie = db.relationship('Movie') # Accès direct à l'objet Movie
