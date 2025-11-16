Configuration and Environment
=============================

Overview
--------
This document describes configuration knobs and environment variables used by the app.

Environment Variables
---------------------
- `SECRET_KEY` (required in production): Flask secret for session signing. Strong random value.
- `FLASK_ENV` (optional): set to `production` under systemd/Gunicorn.

Application Settings
--------------------
Defined in `app/web/app.py`:
- Session lifetime: 4 hours permanent sessions.
- Template folder: `app/web/templates`.

Storage
-------
- Users file: `app/users.json` (auto-created). Can be overridden by passing a custom path to `UserStorage(filepath=...)` where integrated.

Extending Config
----------------
- For future analyzers, prefer a `configs/` directory with `*.toml` or `*.yaml` files, loaded at app startup.


