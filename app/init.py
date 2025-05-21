from flask import Flask
from app.rotas.auth import auth_bp

def create_app():
    app = Flask(__name__)

    #Registrar Blueprints
    app.register_blueprint(auth_bp)

    return app