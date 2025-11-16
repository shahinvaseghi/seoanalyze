from __future__ import annotations

import os
from datetime import timedelta

from flask import Flask, session


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")

    # Secret key from environment or default (to be overridden in production)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.permanent_session_lifetime = timedelta(hours=4)
    
    # Session cookie settings for production (works with multiple Gunicorn workers)
    # Flask uses signed cookies which work across workers when SECRET_KEY is shared
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Register blueprints
    from .auth import auth_bp
    from .routes import routes_bp
    from .users import users_bp
    from .competitors import competitors_bp
    from .keyword_gap import keyword_gap_bp
    from .keyword_gap_v2 import keyword_gap_v2_bp
    from .core_web_vitals import core_web_vitals_bp
    from .technical_seo import technical_seo_bp
    from .search_console import search_console_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(competitors_bp)
    app.register_blueprint(keyword_gap_bp)
    app.register_blueprint(keyword_gap_v2_bp)
    app.register_blueprint(core_web_vitals_bp)
    app.register_blueprint(technical_seo_bp)
    app.register_blueprint(search_console_bp)

    @app.context_processor
    def inject_roles():
        try:
            from app.services.storage import UserStorage
            username = session.get("user")
            is_admin = False
            if username:
                is_admin = UserStorage().is_admin(username)
            return {"is_admin": is_admin}
        except Exception:
            return {"is_admin": False}

    @app.route("/health")
    def health() -> str:
        return "ok"

    return app


app = create_app()


