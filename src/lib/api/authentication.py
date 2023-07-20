from flask import session

from lib.api.errors import Error


def login_required(func):
    def wrapper(*args, **kwargs):

        if 'user' in session:
            return func(*args, **kwargs)
        else:
            return Error('not_authenticated', 'User is not logged in', 401)

    return wrapper
