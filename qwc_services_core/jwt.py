import os
import datetime
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from flask import make_response


def jwt_manager(app, api=None):
    """Setup Flask-JWT-Extended extension for services
       with authenticated access"""
    # https://flask-jwt-extended.readthedocs.io/en/stable/options
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = os.environ.get(
        'JWT_ACCESS_COOKIE_NAME', 'access_token_cookie')
    app.config['JWT_COOKIE_CSRF_PROTECT'] = bool(os.environ.get(
        'JWT_COOKIE_CSRF_PROTECT', False))
    app.config['JWT_SECRET_KEY'] = os.environ.get(
        'JWT_SECRET_KEY', os.urandom(24))

    jwt = JWTManager(app)

    if api:
        # Delegate error handlers to RestPlus because of
        # https://github.com/vimalloc/flask-jwt-extended/issues/86
        jwt._set_error_handler_callbacks(api)

        @api.errorhandler
        def restplus_error_handler(error):
            # JWT error handler will be called afterwards
            return {}

    @jwt.expired_token_loader
    def handle_expired_token():
        # http://flask-jwt-extended.readthedocs.io/en/latest/changing_default_behavior.html
        # resp = redirect('/auth/login')
        # Automatic re-login does't work with SAML, so we prepare
        # for manual re-login
        resp = make_response()
        unset_jwt_cookies(resp)
        return resp

    return jwt
