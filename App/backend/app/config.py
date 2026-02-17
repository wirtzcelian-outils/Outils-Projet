import os

class Config:
    """
    Classe de configuration pour l'application Flask.
    Récupère les valeurs sensibles depuis les variables d'environnement.
    """
    # Clé secrète pour signer les sessions et les tokens (valeur par défaut pour le dev)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_change_me'
    
    # URI de connexion à la base de données (MySQL par défaut)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://user:password@db/app_db'
    
    # Désactive le suivi des modifications des objets (économise de la mémoire)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clé spécifique pour signer les tokens JWT d'authentification
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_dev_secret_change_me'

class TestConfig(Config):
    """
    Configuration spécifique pour les tests unitaires.
    Utilise une base de données en mémoire et désactive les comportements de prod.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
