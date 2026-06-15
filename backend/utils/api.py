"""JSON API wrapper - standard response format."""

from pydantic import BaseModel
from typing import Any


class ApiResponse(BaseModel):
    """Unified JSON response."""
    code: int = 0        # 0 = success, non-zero = error
    message: str = "ok"
    data: Any = None


def ok(data: Any = None, message: str = "ok") -> dict:
    """Success response."""
    return {"code": 0, "message": message, "data": data}


def fail(message: str, code: int = 1, data: Any = None) -> dict:
    """Error response."""
    return {"code": code, "message": message, "data": data}
