app/services/storage.py
=======================

Purpose
-------
Provide minimal JSON-backed user storage with secure password hashing suitable for session-based authentication.

File Location
-------------
`app/services/storage.py`

Data Format
-----------
```json
{
  "users": {
    "admin": {
      "password_hash": "pbkdf2:...",
      "role": "admin"
    }
  }
}
```

Public API
----------
- `class UserStorage(filepath: Optional[str] = None)`
  - Initializes storage. Ensures JSON file exists.

- `create_user(username: str, password: str, role: str = "user") -> None`
  - Creates a user with a hashed password and role. Raises `ValueError` if invalid or already exists.

- `verify_user(username: str, password: str) -> bool`
  - Verifies a plain password against the stored hash. Returns `True` on success.

- `get_user_role(username: str) -> Optional[str]`
  - Returns the role or `None` if user not found.

- `ensure_default_admin(username: str = "admin", password: str = "admin123") -> None`
  - Seeds a default admin if missing. Safe to call multiple times.

Internal Helpers
----------------
- `_ensure_file_exists()`: creates the JSON file and directories if needed.
- `_read() / _write(data)`: safe JSON IO with UTF-8 and pretty-printing.

Notes
-----
- Uses `werkzeug.security.generate_password_hash` and `check_password_hash`.
- Default path: `app/users.json`.
- Consider adding locking if multi-process writes become frequent.


