# File: /home/fcosta/CostaSign/./flask_document_signer/documents/__init__.py
# This file can be empty.
#
# # flask_document_signer/documents/__init__.py
from flask import Blueprint

documents_bp = Blueprint(
    "documents", __name__, template_folder="templates", url_prefix="/documents"
)

from . import routes  # Import routes *after* creating the blueprint
