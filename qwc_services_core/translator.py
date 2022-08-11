import glob
import json
import os


class Translator:
    """Class for translating strings via json files"""

    def __init__(self, app, request):
        """Constructor.

        :param object app: The Flask app
        :param object request: The Flask requst
        """

        supported_locales = list(map(
            lambda path: os.path.basename(path)[0:-5],
            glob.glob('translations/*.json')
        ))

        DEFAULT_LOCALE = os.environ.get('DEFAULT_LOCALE', 'en')
        locale = request.accept_languages.best_match(supported_locales) or DEFAULT_LOCALE

        self.translations = {}
        try:
            path = os.path.join(app.root_path, 'translations/%s.json' % locale)
            with open(path, 'r') as f:
                self.translations = json.load(f)
        except Exception as e:
            app.logger.error(
                "Failed to load translation strings for locale '%s' from %s, loading default locale\n%s"
                % (locale, path, e)
            )
            path = os.path.join(app.root_path, 'translations/%s.json' % DEFAULT_LOCALE)
            with open(path, 'r') as f:
                self.translations = json.load(f)

    def tr(self, msgId):
        """Translate a string.

        :param str msgId: The message id
        """

        parts = msgId.split('.')
        lookup = self.translations
        for part in parts:
            if isinstance(lookup, dict):
                # get next lookup level
                lookup = lookup.get(part)
            else:
                # lookup level too deep
                lookup = None
            if lookup is None:
                # return input msgId if not found
                lookup = msgId
                break

        return lookup
