"""JWT token utilities for API authentication."""

import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, SESSION_EXPIRE_SECONDS


def create_token(user_id: int, username: str, role: str) -> str:
    """Create a JWT access token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=SESSION_EXPIRE_SECONDS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
