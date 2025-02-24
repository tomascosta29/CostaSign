# File: /home/fcosta/CostaSign/./flask_document_signer/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from .forms import LoginForm, RegistrationForm
from functools import wraps
from flask_document_signer.config import Config  # Correct import
from flask_document_signer.models import get_db_connection

auth_bp = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")

# --- Authentication Helper Functions ---


def register_user(username, email, password):
    url = f"{Config.AUTH_SERVICE_URL}/auth/register"
    payload = {"username": username, "email": email, "password": password}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        try:
            error_message = response.json().get("message", str(e))
        except requests.exceptions.JSONDecodeError:
            error_message = str(e)
        return None, error_message


def login_user(username, password):
    url = f"{Config.AUTH_SERVICE_URL}/auth/login"
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def validate_token(token):
    url = f"{Config.AUTH_SERVICE_URL}/auth/validate"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def logout_user(token):
    url = f"{Config.AUTH_SERVICE_URL}/auth/logout"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return True, None
    except requests.exceptions.RequestException as e:
        return False, str(e)


# --- Authentication Decorator ---


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get("token")
        if not token:
            return redirect(url_for("auth.login"))

        validation_response, error = validate_token(token)
        if error:
            session.pop("token", None)
            return redirect(url_for("auth.login"))

        if validation_response is None:
            session.pop("token", None)
            return redirect(url_for("auth.login"))

        user_id = validation_response.get("sub")
        if not user_id:
            session.pop("token", None)
            return redirect(url_for("auth.login"))

        return f(user_id, *args, **kwargs)

    return decorated


# --- Routes ---


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        token_data, error = login_user(username, password)

        if error:
            form.username.errors.append(error)
        elif token_data and token_data.get("token"):
            session["token"] = token_data["token"]
            return redirect(url_for("index"))  # Main index
        else:
            form.username.errors.append("Invalid credentials")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        registration_data, error = register_user(username, email, password)
        if error:
            form.username.errors.append(error)
        else:
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
def logout():
    token = session.get("token")
    if token:
        session.pop("token", None)
        logout_user(token)  # Fire and forget
    return redirect(url_for("index"))
