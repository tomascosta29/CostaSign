# File: /home/fcosta/CostaSign/./flask_document_signer/app.py
from flask import Flask, render_template  # Import render_template
from .config import Config
from .auth.routes import auth_bp
from .documents.routes import documents_bp
from .models import init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)

    with app.app_context():
        init_db()

    # --- ADD THIS BACK ---
    @app.route("/")
    def index():
        return render_template("index.html")

    # ---------------------

    return app


if __name__ == "__main__":
    app = create_app()  # Create app instance *only* when run directly
    app.run(debug=True)
