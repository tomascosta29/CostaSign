# File: /home/fcosta/CostaSign/./flask_document_signer/documents/routes.py
from flask import Blueprint, render_template, request, jsonify, current_app
import os
import hashlib
import sqlite3
from .forms import UploadForm
from flask_document_signer.auth.routes import token_required  # Correct import
from flask_document_signer.models import get_db_connection

documents_bp = Blueprint(
    "documents", __name__, template_folder="templates", url_prefix="/documents"
)

# --- Helper Function ---


def hash_file(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as file:
        while True:
            block = file.read(h.block_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


# --- Routes ---
@documents_bp.route("/sign", methods=["POST"])
@token_required
def sign_document(user_id):
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filename)
        file_hash = hash_file(filename)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO signed_documents (user_id, filename, file_hash) VALUES (?, ?, ?)",
            (user_id, file.filename, file_hash),
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Document signed successfully"}), 200
    return jsonify({"message": "Invalid file"}), 400


@documents_bp.route("/verify", methods=["POST"])
def verify_document():
    signed = None
    user_id = None
    filename = None
    timestamp = None
    message = None

    form = UploadForm()  # Even for verification, use a form for consistency
    if form.validate_on_submit():
        file = form.file.data
        filename_temp = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "temp_verification"
        )
        file.save(filename_temp)
        file_hash = hash_file(filename_temp)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, filename, timestamp FROM signed_documents WHERE file_hash = ?",
            (file_hash,),
        )
        result = cursor.fetchone()
        conn.close()

        os.remove(filename_temp)  # Clean up temporary file

        if result:
            signed = True
            user_id = result["user_id"]
            filename = result["filename"]
            timestamp = result["timestamp"]
            return render_template(
                "documents/verify.html",
                signed=signed,
                user_id=user_id,
                filename=filename,
                timestamp=timestamp,
                form=form,
            )
        else:
            signed = False
            message = "Document not found or has been altered."
            return render_template(
                "documents/verify.html", signed=signed, message=message, form=form
            )
    else:
        message = form.errors or "An error occurred processing the file."
        return render_template(
            "documents/verify.html", signed=signed, message=message, form=form
        )


@documents_bp.route("/sign_page")
@token_required
def sign_page(user_id):
    form = UploadForm()
    return render_template("documents/sign.html", form=form)


@documents_bp.route("/verify_page")
def verify_page():
    form = UploadForm()  # Initialize the form even if it's a GET request
    return render_template("documents/verify.html", signed=None, form=form)
