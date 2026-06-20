"""Custom decorators for role-based access control.

Uses Flask-JWT-Extended claims for role checks. Kept minimal —
complex RBAC should use a dedicated library (e.g. Flask-Principal).
"""

from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_smorest import abort


def role_required(*roles: str):
    """Decorator: require at least one of the given roles.

    Usage:
        @bp.route('/admin')
        @jwt_required()
        @role_required('admin')
        def admin_only():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_roles = claims.get("roles", [])
            if not any(r in user_roles for r in roles):
                abort(403, message="Insufficient permissions")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
