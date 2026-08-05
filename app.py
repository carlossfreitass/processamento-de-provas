"""
Ponto de entrada da aplicação Flask.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    # Application Factory
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    # CORS
    CORS(app)

    # Blueprints
    from app_routes.health import health_bp
    from app_routes.input import input_bp
    from app_routes.pages import pages_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(input_bp)
    app.register_blueprint(pages_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)