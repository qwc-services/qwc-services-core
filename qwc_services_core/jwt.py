import os

from flask_jwt_extended import JWTManager


# Setup the Flask-JWT-Extended extension
def jwt_manager(app):
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get(
      'JWT_SECRET_KEY', 'DEFAULT-SECRET-gtzCqte9ukXeFEkE'
    )

    return JWTManager(app)
