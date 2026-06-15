"""Session utilities - login required decorator"""

from functools import wraps
from fastapi import Request
from fastapi.responses import RedirectResponse


def require_login(func):
    """Decorator to check if user is logged in. Redirects to login if not."""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if "user_id" not in request.session:
            return RedirectResponse(url="/auth/login", status_code=303)
        return await func(request, *args, **kwargs)

    return wrapper
