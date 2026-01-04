from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from .config import Config
import time
from sqlalchemy.exc import OperationalError

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Register blueprints
    from app.routes import auth, movies, lists
    app.register_blueprint(auth.bp)
    app.register_blueprint(movies.bp)
    app.register_blueprint(lists.bp)

    # Ensure tables exist with Retry Logic
    with app.app_context():
        max_retries = 10
        for attempt in range(max_retries):
            try:
                db.create_all()
                # Seed initial data
                from app.routes.movies import seed_movies
                seed_movies()
                print("Database connected and seeded successfully!")
                break
            except OperationalError as e:
                if attempt < max_retries - 1:
                    print(f"Database not ready yet (Attempt {attempt+1}/{max_retries}). Retrying in 5s...")
                    time.sleep(5)
                else:
                    print("Could not connect to database after multiple attempts.")
                    raise e
            except Exception as e:
                print(f"Unexpected error during startup: {e}")
                raise e

    @app.route('/api/health')
    def health():
        return {"status": "ok"}

    return app
