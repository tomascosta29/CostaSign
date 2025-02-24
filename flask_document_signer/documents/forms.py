# File: /home/fcosta/CostaSign/./flask_document_signer/documents/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired


class UploadForm(FlaskForm):
    file = FileField(
        "Document",
        validators=[
            FileRequired(),
            FileAllowed(["pdf", "txt", "doc", "docx"], "Allowed file types only!"),
        ],
    )
