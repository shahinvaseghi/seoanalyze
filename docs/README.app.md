app/web/app.py
===============

Purpose
-------
Create and configure the Flask application, register blueprints, and expose a health endpoint.

Key Elements
------------
- `create_app() -> Flask`
  - Builds the Flask instance, sets `secret_key` from env `SECRET_KEY` (dev default otherwise), configures session lifetime, and registers `auth` and `routes` blueprints.
- `@app.route('/health')`
  - Returns `ok` for liveness checks.

Environment
-----------
- `SECRET_KEY`: must be set in production to a strong random value.
- `FLASK_ENV`: recommended `production` under systemd/Gunicorn.

Notes
-----
- `app = create_app()` at the bottom provides the WSGI entrypoint for Gunicorn: `app.web.app:app`.


