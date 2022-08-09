from functools import wraps
from flask import abort
import flask_login


def private_space_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if flask_login.current_user.have_private_space:
            return function(*args, **kwargs)

        else:
            abort(404)

    return decorated_function
