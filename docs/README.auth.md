app/web/auth.py
================

Purpose
-------
Provide login/logout routes and integrate with session-based authentication.

Blueprint
---------
- `auth_bp = Blueprint('auth', __name__)`

Routes
------
- `@auth_bp.route('/login', methods=['GET', 'POST'])`
  - GET: renders `login.html`.
  - POST: reads `username` and `password` from form, uses `UserStorage.verify_user` to authenticate.
    - On success: clears session, sets `session['user'] = username`, marks session as permanent, redirects to `routes.dashboard`.
    - On failure: flashes `Invalid credentials` and re-renders the login form.

- `@auth_bp.route('/logout', methods=['GET'])`
  - Clears session and redirects to the login page.

Dependencies
------------
- `app.services.storage.UserStorage` for credential checking.
- Flask session, flash, redirect utilities.

Security Notes
--------------
- Passwords are never stored in plaintext. Verification uses hashed passwords.
- Consider adding rate-limiting and CSRF protection for form posts in future iterations.


