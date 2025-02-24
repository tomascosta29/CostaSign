# flask_document_signer/models.py

import sqlite3
from flask_document_signer.config import Config  # Import Config


def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_URI)  # Use Config for the database path
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the users table exists.  Create it if necessary (adapt as needed).
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create the documents table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


# Example function to get all documents for a user (you'll use this later)
def get_documents_for_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE user_id = ?", (user_id,))
    documents = cursor.fetchall()
    conn.close()
    return documents


def get_document_by_id(document_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
    document = cursor.fetchone()
    conn.close()
    return document


def insert_document(user_id, filename, original_filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, filename, original_filename) VALUES (?, ?, ?)",
        (user_id, filename, original_filename),
    )
    conn.commit()
    document_id = cursor.lastrowid  # Get the ID of the newly inserted document
    conn.close()
    return document_id
