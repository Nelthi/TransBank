from flask import Flask
from app.models import db
from flasgger import Swagger  # Importation de Swagger pour la documentation de l'API
from app.routes import auth_bp
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation de la doc Swagger
    swagger = Swagger(app)

    db.init_app(app)

    # Enregistrement des blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()  # Crée les tables dans PostgreSQL si elles n'existent pas

    return app