from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.services.storage import UserStorage


users_bp = Blueprint("users", __name__, url_prefix="/users")


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        username = session.get("user")
        if not username:
            return redirect(url_for("auth.login"))
        storage = UserStorage()
        if not storage.is_admin(username):
            flash("Admin access required", "error")
            return redirect(url_for("routes.dashboard"))
        return func(*args, **kwargs)

    return wrapper


@users_bp.route("/")
@admin_required
def list_users():
    storage = UserStorage()
    users = storage.list_users()
    return render_template("users/list.html", users=users)


@users_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create_user():
    storage = UserStorage()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")
        try:
            storage.create_user(username, password, role)
            flash("User created", "success")
            return redirect(url_for("users.list_users"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("users/form.html", mode="create", user={"username": "", "role": "user"})


@users_bp.route("/<username>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(username: str):
    storage = UserStorage()
    if request.method == "POST":
        password = request.form.get("password") or None
        role = request.form.get("role") or None
        try:
            storage.update_user(username, password=password, role=role)
            flash("User updated", "success")
            return redirect(url_for("users.list_users"))
        except ValueError as e:
            flash(str(e), "error")
    # Fetch current role to prefill form
    role = storage.get_user_role(username) or "user"
    return render_template("users/form.html", mode="edit", user={"username": username, "role": role})


@users_bp.route("/<username>/delete", methods=["POST"])
@admin_required
def delete_user(username: str):
    storage = UserStorage()
    if username == session.get("user"):
        flash("You cannot delete the currently logged-in user", "error")
        return redirect(url_for("users.list_users"))
    storage.delete_user(username)
    flash("User deleted", "success")
    return redirect(url_for("users.list_users"))


