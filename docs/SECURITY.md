Security Guide
==============

Secrets
-------
- Set `SECRET_KEY` to a strong random value in production (not committed to VCS).
- Rotate secrets periodically.

Authentication
--------------
- Passwords are hashed with Werkzeug. Never store plain passwords.
- Consider account lockout or rate limiting on repeated login failures.

Transport
---------
- Terminate TLS at Nginx with Let's Encrypt or Cloudflare certificates (see `docs/README_HTTPS.md`).

Sessions
--------
- Use secure cookies (HTTPS) in production; set appropriate cookie flags via Flask configuration if exposing over the internet.

Hardening
---------
- Run Gunicorn bound to localhost; expose only via Nginx.
- Keep packages up to date; pin and audit dependencies.


