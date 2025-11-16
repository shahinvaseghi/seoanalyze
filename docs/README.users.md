Admin Users Management
======================

Purpose
-------
Provide admin-only user management (list/create/edit/delete) backed by JSON storage.

Blueprint
---------
- File: `app/web/users.py`
- Name: `users_bp` with `url_prefix='/users'`

Access Control
--------------
- Decorator: `admin_required`
  - Redirects unauthenticated users to login
  - Redirects non-admins to dashboard with a flash error

Routes
------
- `GET /users/` → `list_users()`
  - Renders `users/list.html` with user map `{username: {role}}`

- `GET|POST /users/create` → `create_user()`
  - GET renders form, POST creates a user via `UserStorage.create_user(username, password, role)`

- `GET|POST /users/<username>/edit` → `edit_user(username)`
  - GET pre-fills role; POST updates role and/or password using `UserStorage.update_user(...)`

- `POST /users/<username>/delete` → `delete_user(username)`
  - Prevents deleting the currently logged-in user

Templates
---------
- `app/web/templates/users/list.html` — table of users with edit/delete actions
- `app/web/templates/users/form.html` — form for create/edit with role select (user/admin)

Storage API
-----------
- See `docs/README.storage.md`
- Additional methods used: `list_users()`, `update_user()`, `delete_user()`, `is_admin()`

Dashboard Link Visibility
-------------------------
- `app/web/app.py` injects `is_admin` into templates via a context processor
- `dashboard.html` shows the Users link only if `is_admin` is `True`


