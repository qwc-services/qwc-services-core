import logging
import os
from flask import Flask, session, request, url_for
from qwc_services_core.tenant_handler import TenantHandler, \
    TenantPrefixMiddleware, TenantSessionInterface


AUTH_PATH = os.environ.get('AUTH_PATH', '/auth')

# Flask application
app = Flask(__name__)
app.secret_key = 'test'

app.wsgi_app = TenantPrefixMiddleware(app.wsgi_app)
app.session_interface = TenantSessionInterface(os.environ)

# routes
@app.route('/')
def home():
    return '<a href="%s">login</a> | <a href="%s">test</a>' % (
        url_for('login'), url_for('test_html'))


@app.route('/login')
def login():
    auth_path = request.script_root + AUTH_PATH + '/login'
    return "Calling %s" % auth_path


@app.route('/pages/test.html')
def test_html():
    session['test'] = 'test'
    return "Cookie path: %s" % app.session_interface.get_cookie_path(app)


# local webserver
if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='localhost', port=5031, debug=True)

# Usage example with uwsgi:
# uwsgi --http-socket :9090 --plugins python3 --protocol uwsgi --wsgi-disable-file-wrapper --master --mount /base=middleware-test:app --manage-script-name
