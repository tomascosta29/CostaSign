# File: /home/fcosta/CostaSign/./flask_document_signer/config.py
import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-hardcoded-secret-key"
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL") or "http://localhost:8080"
    DATABASE_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "signing.db"
    )
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_PATH  # Add this line!
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        False  # Good practice to disable this if not needed
    )

    DATABASE_URI = "document_signing.db"  # Relative path to the db
    DOCUMENT_STORAGE_PATH = os.path.join(
        os.getcwd(), "document_storage"
    )  # Absolute Path to storage


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # ... production settings ...


class TestingConfig(Config):
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory for tests
