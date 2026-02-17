import pytest
from app.models import User, List
from app import db, bcrypt

# Tests unitaires pour les Modèles de Données (SQLAlchemy)

def test_password_hashing(app):
    """
    Vérifie que le mot de passe n'est jamais stocké en clair.
    """
    password = "secret_password"
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user = User(username="hashuser", password_hash=hashed)
    
    assert user.password_hash != password
    assert bcrypt.check_password_hash(user.password_hash, password) is True

def test_user_list_relationship(app):
    """
    Vérifie la relation entre User et List.
    Un utilisateur doit pouvoir avoir plusieurs listes.
    """
    with app.app_context():
        # Création User
        user = User(username="relationuser", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        
        # Ajout de listes
        l1 = List(user_id=user.id, name="Liste 1")
        l2 = List(user_id=user.id, name="Liste 2")
        db.session.add_all([l1, l2])
        db.session.commit()
        
        # Vérification via la relation SQLAlchemy
        # Il faut re-récupérer l'user pour avoir ses listes à jour
        fetched_user = User.query.get(user.id)
        assert len(fetched_user.lists) == 2
        assert fetched_user.lists[0].name == "Liste 1"
        assert fetched_user.lists[1].name == "Liste 2"
