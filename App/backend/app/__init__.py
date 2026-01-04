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
    from app.routes import auth, movies, lists, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(movies.bp)
    app.register_blueprint(lists.bp)
    app.register_blueprint(admin.bp)

    # Ensure tables exist with Retry Logic
    with app.app_context():
        max_retries = 10
        for attempt in range(max_retries):
            try:
                db.create_all()
                
                # Auto-migrate schema
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE movies ADD COLUMN release_date VARCHAR(20)"))
                        conn.execute(text("ALTER TABLE movies ADD COLUMN is_custom BOOLEAN DEFAULT 1"))
                        conn.commit()
                        print("Added release_date and is_custom columns.")
                except Exception as migration_error:
                    print(f"Migration note: {migration_error}")
                
                # Fix Foreign Key Constraint for Cascade Delete (Safe Patch)
                try:
                    with db.engine.connect() as conn:
                        # Check if constraint exists effectively or just try to drop/add
                        # Dropping implies it might exist incorrectly. 
                        # We use a specific name 'list_items_ibfk_2'.
                        # NOTE: In production we'd check information_schema, but here we just try-except.
                        
                        # ALREADY APPLIED CHECK? No easy way without querying schema.
                        # We will try to DROP and ADD. If DROP fails, maybe it doesn't exist.
                        # If ADD fails, maybe it exists. 
                        
                        # Better approach: Try to ADD with CASCADE. If fails, it might exist without it.
                        # Let's try DROP then ADD.
                         
                        try:
                            conn.execute(text("ALTER TABLE list_items DROP FOREIGN KEY list_items_ibfk_2"))
                            print("Dropped old movie_id FK constraint.")
                        except Exception:
                            pass # Might not exist or different name
                            
                        # Re-add with CASCADE
                        conn.execute(text("ALTER TABLE list_items ADD CONSTRAINT list_items_ibfk_2 FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE"))
                        conn.commit()
                        print("Applied CASCADE delete to list_items.movie_id")
                except Exception as fk_error:
                    # If it fails, maybe it already exists and duplicate constraint?
                    print(f"FK Fix note: {fk_error}")

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
