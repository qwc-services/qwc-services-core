
def app_nocache(app):
    """ Adds various cache-disabling headers to all responses returned by the
        application
    :param Flask app: A flask application
    """
    @app.after_request
    def add_header(r):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r
