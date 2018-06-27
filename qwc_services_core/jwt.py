from flask_jwt_extended import JWTManager


# Setup the Flask-JWT-Extended extension
def jwt_manager(app):
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    app.config['JWT_SECRET_KEY'] = 'a#`\xbf\xd1-\x10\xa8\xf1\xaa\x9bJ\xd6\x13\x1e\x1e,\xda\xe4\xc1\xa7\xfd\xab:'  # Change this!

    return JWTManager(app)
