import os
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
        'JWT_COOKIE_CSRF_PROTECT', 'True')).upper() == "TRUE"
    app.config['JWT_CSRF_CHECK_FORM'] = True
    app.config['JWT_SECRET_KEY'] = os.environ.get(
        'JWT_SECRET_KEY', os.urandom(24))
    app.config['JWT_ACCESS_COOKIE_PATH'] = os.environ.get(
        'JWT_ACCESS_COOKIE_PATH', '/')
    app.config['JWT_IDENTITY_CLAIM'] = "qwc_identity"

    jwt = JWTManager(app)

    def handle_bad_jwt():
        redirect_url = request.url
        app.logger.warn("Redirecting to %s and unsetting JWT cookie" % redirect_url)
        resp = redirect(redirect_url)
        unset_jwt_cookies(resp)
        # Also unset cookie without trailing slash
        # Fixes possible endless redirect loops if for whatever reason both access cookies for Paths with and without trailing / were set
        access_cookie_path = app.config['JWT_ACCESS_COOKIE_PATH']
        if access_cookie_path.endswith("/") and access_cookie_path != "/":
            app.config['JWT_ACCESS_COOKIE_PATH'] = app.config['JWT_ACCESS_COOKIE_PATH'].rstrip("/")
            unset_jwt_cookies(resp)
        return resp

    @app.after_request
    def handle_jwt_exceptions(resp):
        # If error is a JWT error, redirect to login
        if resp.status_code == 500 and resp.content_type == "application/json":
            data = json.loads(resp.data)
            if "message" in data and data["message"].startswith("jwtexception:"):
                return handle_bad_jwt()

        return resp

    @app.before_request
    def set_jwt_access_cookie_path():
        # If app.session_interface is a TenantSessionInterface, JWT_ACCESS_COOKIE_PATH is set regarding tenant
        # Else it takes value from SESSION_COOKIE_PATH config var, or APPLICATION_ROOT or /
        # https://flask.palletsprojects.com/en/3.0.x/api/#flask.sessions.SessionInterface.get_cookie_path
        from .tenant_handler import TenantSessionInterface
        if isinstance(app.session_interface, TenantSessionInterface):
            if app.session_interface.is_multi():
                app.session_interface.get_cookie_path(app)

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
        # Redirect to login on expired token
        app.logger.warn("Expired token")
        return handle_bad_jwt()

    @jwt.invalid_token_loader
    def handle_invalid_token(err):
        # Redirect to login on token error
        app.logger.warn("Invalid token: %s" % str(err))
        return handle_bad_jwt()

    @jwt.unauthorized_loader
    def unauthorized(err):
        # Redirect to requested page on authorized error (i.e. CSRF token error)
        app.logger.warn("Unauthorized: %s" % str(err))
        return redirect(request.url)

    return jwt
