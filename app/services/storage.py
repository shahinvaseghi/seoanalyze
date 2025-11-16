import json
import os
from typing import Dict, Optional
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash


DEFAULT_USERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.json")


class UserStorage:
    """Simple JSON-backed user storage.

    Structure of users.json:
    {
        "users": {
            "admin": {
                "password_hash": "...",
                "role": "admin"
            }
        }
    }
    """

    def __init__(self, filepath: Optional[str] = None) -> None:
        self.filepath = filepath or DEFAULT_USERS_PATH
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not os.path.exists(self.filepath):
            directory = os.path.dirname(self.filepath)
            os.makedirs(directory, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({"users": {}}, f, ensure_ascii=False, indent=2)

    def _read(self) -> Dict:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_user(self, username: str, password: str, role: str = "user") -> None:
        username = username.strip()
        if not username or not password:
            raise ValueError("Username and password are required")

        data = self._read()
        users = data.setdefault("users", {})
        if username in users:
            raise ValueError("User already exists")

        users[username] = {
            "password_hash": generate_password_hash(password),
            "role": role,
        }
        self._write(data)

    def verify_user(self, username: str, password: str) -> bool:
        data = self._read()
        user = data.get("users", {}).get(username)
        if not user:
            return False
        return check_password_hash(user.get("password_hash", ""), password)

    def get_user_role(self, username: str) -> Optional[str]:
        data = self._read()
        user = data.get("users", {}).get(username)
        return user.get("role") if user else None

    def list_users(self) -> Dict[str, Dict[str, str]]:
        data = self._read()
        # Never expose password hashes to callers that may serialize responses
        users_safe: Dict[str, Dict[str, str]] = {}
        for uname, uinfo in data.get("users", {}).items():
            users_safe[uname] = {"role": uinfo.get("role", "user")}
        return users_safe

    def update_user(self, username: str, password: Optional[str] = None, role: Optional[str] = None) -> None:
        data = self._read()
        users = data.get("users", {})
        if username not in users:
            raise ValueError("User not found")
        if password:
            users[username]["password_hash"] = generate_password_hash(password)
        if role:
            users[username]["role"] = role
        self._write(data)

    def delete_user(self, username: str) -> None:
        data = self._read()
        users = data.get("users", {})
        if username in users:
            del users[username]
            self._write(data)

    def is_admin(self, username: str) -> bool:
        return self.get_user_role(username) == "admin"

    def ensure_default_admin(self, username: str = "admin", password: str = "admin123") -> None:
        data = self._read()
        users = data.setdefault("users", {})
        if username not in users:
            users[username] = {
                "password_hash": generate_password_hash(password),
                "role": "admin",
            }
            self._write(data)
    
    # ==================== Google Search Console OAuth ====================
    
    def save_gsc_tokens(self, username: str, tokens: Dict) -> None:
        """Save Google Search Console OAuth tokens for user"""
        data = self._read()
        users = data.get("users", {})
        
        if username not in users:
            raise ValueError("User not found")
        
        users[username]["gsc_tokens"] = tokens
        self._write(data)
    
    def get_gsc_tokens(self, username: str) -> Optional[Dict]:
        """Get Google Search Console OAuth tokens for user"""
        data = self._read()
        user = data.get("users", {}).get(username)
        
        if not user:
            return None
        
        return user.get("gsc_tokens")
    
    def has_gsc_connection(self, username: str) -> bool:
        """Check if user has connected Search Console"""
        tokens = self.get_gsc_tokens(username)
        return bool(tokens and tokens.get("access_token"))
    
    def disconnect_gsc(self, username: str) -> None:
        """Remove Google Search Console connection for user"""
        data = self._read()
        users = data.get("users", {})
        
        if username in users and "gsc_tokens" in users[username]:
            del users[username]["gsc_tokens"]
            self._write(data)
    
    def save_gsc_properties(self, username: str, properties: list) -> None:
        """Save list of Search Console properties user has access to"""
        data = self._read()
        users = data.get("users", {})
        
        if username not in users:
            raise ValueError("User not found")
        
        if "gsc_tokens" not in users[username]:
            users[username]["gsc_tokens"] = {}
        
        users[username]["gsc_tokens"]["properties"] = properties
        users[username]["gsc_tokens"]["properties_updated_at"] = datetime.now().isoformat()
        self._write(data)


