Templates: login.html and dashboard.html
=======================================

Purpose
-------
Provide a minimal, modern-looking UI for authentication and a protected landing page.

Files
-----
- `app/web/templates/login.html`
  - A POST form with `username` and `password` inputs and a submit button.
  - Displays flashed error messages (e.g., invalid credentials).
  - Inline CSS for a simple dark theme card layout.

- `app/web/templates/dashboard.html`
  - Minimal protected page showing signed-in username and a `Logout` link.
  - Serves as a starting point for adding analysis pages.

Notes
-----
- For production styling, consider extracting inline CSS into static files and adding a build process.


