from functools import wraps

from flask import request
from flask_login import current_user


def conditional_login_required(func):
    from flask import current_app
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in ['OPTIONS']:# EXEMPT_METHODS:
            return func(*args, **kwargs)
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        if 'DEFAULT_ANONYMOUS_READ' in current_app.config and current_app.config['DEFAULT_ANONYMOUS_READ']:
            return func(*args, **kwargs)
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
