# File: /home/fcosta/CostaSign/./flask_document_signer/documents/routes.py
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    jsonify,
    current_app,
    send_file,
    abort,
    redirect,
    url_for,
)
import os
import hashlib
import uuid
from .forms import UploadForm
from flask_document_signer.auth.routes import token_required  # Correct import
from flask_document_signer.models import get_db_connection
from flask_document_signer.models import (
    get_documents_for_user,
    get_document_by_id,
    insert_document,
)
from flask_document_signer.config import Config

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
@documents_bp.route("/sign", methods=["GET", "POST"])
@token_required
def sign_document(user_id):
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "error")  # Use flash for messages
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(request.url)
        if file:
            # Generate a unique filename
            unique_filename = str(uuid.uuid4())
            file_name, file_extension = os.path.splitext(file.filename)
            filename_on_disk = f"{unique_filename}{file_extension}"

            original_filename = file.filename  # Store for display later

            # Save the file
            filepath = os.path.join(Config.DOCUMENT_STORAGE_PATH, filename_on_disk)
            file.save(filepath)

            # Calculate the hash of the file's content
            with open(filepath, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Insert into the database using the function from models.py
            document_id = insert_document(
                user_id, filename_on_disk, original_filename
            )  # Use the function
            flash("File uploaded and signed successfully!", "success")
            return redirect(url_for("documents.my_documents"))

    return render_template("documents/sign.html")


# ... (other imports and routes) ...
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
        # Create the UPLOAD_FOLDER if it doesn't exist
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        filename_temp = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "temp_verification"
        )
        file.save(filename_temp)
        file_hash = hash_file(filename_temp)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, original_filename, upload_date FROM documents WHERE filename = ?",  # Corrected query
            (file_hash,),
        )
        result = cursor.fetchone()
        conn.close()

        os.remove(filename_temp)  # Clean up temporary file

        if result:
            signed = True
            user_id = result["user_id"]
            filename = result["original_filename"]  # Use original_filename
            timestamp = result["upload_date"]  # Use upload_date
            flash("Document is valid", "success")
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
            flash(message, "error")  # flash message
            return render_template(
                "documents/verify.html", signed=signed, message=message, form=form
            )
    else:
        message = form.errors or "An error occurred processing the file."
        flash(message, "error")
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


@documents_bp.route("/my_documents")
@token_required
def my_documents(user_id):
    documents = get_documents_for_user(user_id)
    return render_template("documents/my_documents.html", documents=documents)


@documents_bp.route("/download/<int:document_id>")
@token_required
def download_document(user_id, document_id):
    document = get_document_by_id(document_id)

    if not document:
        abort(404, description="Document not found")  # 404 Not Found

    # Authorization check: Make sure the document belongs to the logged-in user
    if document["user_id"] != user_id:
        abort(403, description="Unauthorized")  # 403 Forbidden

    file_path = os.path.join(Config.DOCUMENT_STORAGE_PATH, document["filename"])

    if not os.path.exists(file_path):
        abort(404, description="File not found on server")

    return send_file(
        file_path, as_attachment=True, download_name=document["original_filename"]
    )
