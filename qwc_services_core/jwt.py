import os
import datetime
import json
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from flask import redirect, request
from jwt.exceptions import PyJWTError


def jwt_manager(app, api=None):
    """Setup Flask-JWT-Extended extension for services
       with authenticated access"""
    # https://flask-jwt-extended.readthedocs.io/en/stable/options
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = os.environ.get(
        'JWT_ACCESS_COOKIE_NAME', 'access_token_cookie')
    app.config['JWT_COOKIE_CSRF_PROTECT'] = str(os.environ.get(
        'JWT_COOKIE_CSRF_PROTECT', 'False')).upper() == "TRUE"
    app.config['JWT_CSRF_CHECK_FORM'] = True
    app.config['JWT_SECRET_KEY'] = os.environ.get(
        'JWT_SECRET_KEY', os.urandom(24))

    jwt = JWTManager(app)

    @app.after_request
    def handle_jwt_exceptions(resp):
        # If error is a JWT error, unset JWT cookies and redirect to requested URL
        if resp.status_code == 500 and resp.content_type == "application/json":
            data = json.loads(resp.data)
            if "message" in data and data["message"].startswith("jwtexception:"):
                resp = redirect(request.url)
                unset_jwt_cookies(resp)
                return resp

        return resp

    if api:

        @api.errorhandler
        def restplus_error_handler(error):
            # If error is a JWT error, prefix message with jwtexception: so that it
            # can be recognized in handle_jwt_exceptions above
            if isinstance(error, PyJWTError):
                return {"message": "jwtexception:%s" % str(error)}

            return {}

    @jwt.expired_token_loader
    def handle_expired_token(jwtheader, jwtdata):
        # Unset cookies and redirect to requested page on expired token
        resp = redirect(request.url)
        unset_jwt_cookies(resp)
        return resp

    @jwt.invalid_token_loader
    def handle_invalid_token(err):
        # Unset cookies and redirect to requested page on token error
        resp = redirect(request.url)
        unset_jwt_cookies(resp)
        return resp

    return jwt
