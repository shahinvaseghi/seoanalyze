requirements.txt
================

Dependencies
------------
- `Flask==3.0.0`: Web framework providing routing, request/response handling, and templating via Jinja2.
- `Werkzeug==3.0.1`: WSGI utilities; used here for secure password hashing utilities.
- `itsdangerous==2.1.2`: Cryptographic signing (Flask dependency).
- `Jinja2==3.1.2`: Template engine used by Flask.
- `click==8.1.7`: Command-line utilities (Flask dependency).

Notes
-----
- Gunicorn is installed directly into the virtualenv for production serving under systemd.
- Pin versions for reproducibility; regularly update and test.


