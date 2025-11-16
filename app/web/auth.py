from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, session, url_for, flash

from app.services.storage import UserStorage


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    storage = UserStorage()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if storage.verify_user(username, password):
            session.clear()
            session["user"] = username
            session.permanent = True
            return redirect(url_for("routes.dashboard"))
        flash("Invalid credentials", "error")
    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


