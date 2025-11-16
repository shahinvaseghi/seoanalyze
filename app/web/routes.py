from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import Blueprint, render_template, session, redirect, url_for
from app.services.storage import UserStorage


routes_bp = Blueprint("routes", __name__)

F = TypeVar("F", bound=Callable[..., object])


def login_required(view: F) -> F:  # type: ignore[override]
    @wraps(view)
    def wrapped(*args, **kwargs):  # type: ignore[misc]
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped  # type: ignore[return-value]


@routes_bp.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("routes.dashboard"))
    return redirect(url_for("auth.login"))


@routes_bp.route("/dashboard")
@login_required
def dashboard():
    username = session.get("user")
    is_admin = UserStorage().is_admin(username) if username else False
    return render_template("dashboard.html", username=username, is_admin=is_admin)


