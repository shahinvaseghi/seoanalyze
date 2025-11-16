app/web/routes.py
=================

Purpose
-------
Provide the index and dashboard views and a reusable `login_required` decorator.

Key Elements
------------
- `routes_bp = Blueprint('routes', __name__)`

- `login_required(view)`
  - Decorator wrapping a view to enforce that `session['user']` exists; otherwise redirects to `auth.login`.

Routes
------
- `@routes_bp.route('/') -> index()`
  - Redirects authenticated users to `/dashboard`; unauthenticated users to `/login`.

- `@routes_bp.route('/dashboard') -> dashboard()`
  - Protected by `@login_required`. Renders `dashboard.html` with `username` from the session.

Notes
-----
- Keep business logic out of views; delegate to services/analyzers in future modules.


