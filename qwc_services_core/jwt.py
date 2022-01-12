import os
import datetime
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from flask import make_response, Response, redirect, request


class JwtErrorHandlerProxy:
    def __init__(self, api):
        self.api = api

    def errorhandler(self, errortype):
        return lambda jwt_callback: self.api.errorhandler(errortype)(lambda error: self.jwt_callback_wrapper(jwt_callback, error))

    def jwt_callback_wrapper(self, jwt_callback, error):
        result = jwt_callback(error)
        # flask_restx error handler expects a plain object with an 'message' field
        # See flask_restx/api.py@handle_error
        if isinstance(result[0], Response):
            return {"message": result[0].json["msg"]}, result[1]
        return result


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

    if api:
        api.__jwt_error_handler_proxy = JwtErrorHandlerProxy(api)

        # Delegate error handlers to flask_restx because of
        # https://github.com/vimalloc/flask-jwt-extended/issues/86
        jwt._set_error_handler_callbacks(api.__jwt_error_handler_proxy)

        @api.errorhandler
        def restplus_error_handler(error):
            # JWT error handler will be called afterwards
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
