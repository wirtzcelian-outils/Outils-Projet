from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from .config import Config
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

# Initialisation des extensions Flask (Base de données, Migration, JWT, Hachage mdp)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    """
    Fonction Factory pour créer et configurer l'instance de l'application Flask.
    Permet une meilleure gestion des tests et des configurations multiples.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions avec l'instance de l'application
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # Configuration de CORS pour autoriser les requêtes cross-origin
    CORS(app)
    
    # Configuration de Swagger pour la documentation de l'API
    from flasgger import Swagger
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API Documentation",
            "description": "Classement Cine API",
            "version": "1.0.0"
        },
    }
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "hide_top_bar": True,
        # Masquer la barre supérieure et le lien JSON pour une interface plus propre
        "footer_text": "<style>.topbar { display: none !important; } a[href$='/apispec_1.json'] { display: none !important; }</style>",
    }
    
    swagger = Swagger(app, template=swagger_template, config=swagger_config)

    # Enregistrement des Blueprints (les différentes parties de l'API)
    from app.routes import auth, movies, lists, admin, profile
    app.register_blueprint(auth.bp)
    app.register_blueprint(movies.bp)
    app.register_blueprint(lists.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(profile.bp)

    # Logique de démarrage : vérification de la connexion DB et migrations automatiques
    # Cette logique est ignorée lors des tests pour éviter de bloquer l'exécution
    if not app.config.get('TESTING'):
        with app.app_context():
            max_retries = 10
            for attempt in range(max_retries):
                try:
                    # Création des tables si elles n'existent pas
                    db.create_all()
                    
                    # Migrations manuelles / correctifs de schéma
                    try:
                        with db.engine.connect() as conn:
                            # Ajout de colonnes manquantes pour les versions précédentes
                            conn.execute(text("ALTER TABLE movies ADD COLUMN release_date VARCHAR(20)"))
                            conn.execute(text("ALTER TABLE movies ADD COLUMN is_custom BOOLEAN DEFAULT 1"))
                            conn.commit()
                            print("Added release_date and is_custom columns.")
                    except Exception as migration_error:
                        # Ignorer si les colonnes existent déjà
                        print(f"Migration note: {migration_error}")
                    
                    # Correction des contraintes de clé étrangère (Cascade Delete)
                    try:
                        with db.engine.connect() as conn:
                            try:
                                conn.execute(text("ALTER TABLE list_items DROP FOREIGN KEY list_items_ibfk_2"))
                                print("Dropped old movie_id FK constraint.")
                            except Exception:
                                pass
                                
                            conn.execute(text("ALTER TABLE list_items ADD CONSTRAINT list_items_ibfk_2 FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE"))
                            conn.commit()
                            print("Applied CASCADE delete to list_items.movie_id")
                    except Exception as fk_error:
                        print(f"FK Fix note: {fk_error}")

                    # Peuplement initial de la base de données
                    from app.routes.movies import seed_movies
                    seed_movies()
                    print("Database connected and seeded successfully!")
                    break
                except OperationalError as e:
                    # Gestion de l'attente si la base de données n'est pas encore prête (ex: démarrage Docker)
                    if attempt < max_retries - 1:
                        print(f"Database not ready yet (Attempt {attempt+1}/{max_retries}). Retrying in 5s...")
                        time.sleep(5)
                    else:
                        print("Could not connect to database after multiple attempts.")
                        raise e
                except Exception as e:
                    print(f"Unexpected error during startup: {e}")
                    raise e

    # Endpoint de santé pour vérifier que l'API tourne
    @app.route('/api/health')
    def health():
        return {"status": "ok"}

    return app
