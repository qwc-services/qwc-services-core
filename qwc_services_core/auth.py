"""Authentication helper functions
"""
import os
from flask import request
from .jwt import jwt_manager
from flask_jwt_extended import jwt_optional, get_jwt_identity


# Accept user name passed in Basic Auth header
# (password has to checkded before!)
ALLOW_BASIC_AUTH_USER = os.environ.get('ALLOW_BASIC_AUTH_USER', 'False') \
    .lower() in ('t', 'true')


def auth_manager(app, api=None):
    """Authentication setup for Flask app"""
    # Setup the Flask-JWT-Extended extension
    return jwt_manager(app, api)


def optional_auth(fn):
    """Authentication view decorator"""
    return jwt_optional(fn)


def get_auth_user():
    """Get username in authenticated request"""
    username = get_jwt_identity()
    if not username and ALLOW_BASIC_AUTH_USER:
        auth = request.authorization
        if auth:
            # We don't check password. Already done by WAF.
            username = auth.username
    return username
