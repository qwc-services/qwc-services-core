import os
import re
from flask import json
from werkzeug.utils import safe_join


class RuntimeConfig:
    '''Runtime configuration helper class
    '''

    @staticmethod
    def config_file_path(service, tenant):
        """Return path to permissions JSON file for a tenant.

        :param str servcie: Service name
        :param str tenant: Tenant ID
        """
        config_path = os.environ.get('CONFIG_PATH', 'config')
        filename = '%sConfig.json' % service
        return safe_join(config_path, tenant, filename)

    def __init__(self, service, logger, config_file_is_optional = true):
        self.service = service
        self.logger = logger
        self.config = None
        self.config_file_is_optional = config_file_is_optional

    def set_config(self, config):
        """ Directly sets the internal config object. """
        self.config = config
        return self

    def read_config(self, tenant):
        """Read service config for a tenant from a JSON file.

        :param str tenant: Tenant ID
        """
        runtime_config_path = RuntimeConfig.config_file_path(
            self.service, tenant
        )
        self.logger.info(
            "Reading runtime config '%s'" % runtime_config_path
        )
        try:
            with open(runtime_config_path, encoding='utf-8') as fh:
                data = fh.read()
                # Replace env variables
                dataout = ENVVAR_PATTERN.sub(envrepl, data)
                self.config = json.loads(dataout)
        except Exception as e:
            if self.config_file_is_optional:
                self.logger.info(
                    "Could not load runtime config '%s':\n%s\nHowever ignoring due to option config_file_is_optional being set to true" %
                    (runtime_config_path, e)
                )
            else:
                self.logger.error(
                    "Could not load runtime config '%s':\n%s" %
                    (runtime_config_path, e)
                )
            self.config = {}
        return self

    def tenant_config(self, tenant):
        return self.read_config(tenant)

    def get(self, name, default=None):
        val = self.config.get('config', {}).get(name, default)
        # Optional override from env var
        envval = os.environ.get(name.upper())
        if envval is not None:
            # Convert from string
            try:
                if val is None:
                    # unkown type --> no conversion
                    val = envval
                elif type(val) in (list, dict):
                    val = json.loads(envval)
                elif type(val) is bool:
                    # convert string to boolean
                    # cf. deprecated distutils.util.strtobool
                    #   https://docs.python.org/3.9/distutils/apiref.html#distutils.util.strtobool
                    if envval.lower() in (
                        'true', 't', '1', 'on', 'yes', 'y'
                    ):
                        val = True
                    elif envval.lower() in (
                        'false', 'f', '0', 'off', 'no', 'n', ''
                    ):
                        # NOTE: also convert empty string to False
                        #       to support legacy env configs
                        #       (bool("") => False)
                        val = False
                    else:
                        raise Exception(
                            "Unknown boolean value for '%s'" % envval
                        )
                else:
                    val = type(val)(envval)
            except Exception as e:
                self.logger.warning(
                    "Could not convert config override "
                    "from env '%s=%s' to %s:\n%s" %
                    (name.upper(), envval, type(val), e)
                )

        return val

    def resources(self):
        return self.config.get('resources')

    def resource(self, name):
        return self.config.get('resources', {}).get(name)


ENVVAR_PATTERN = re.compile(r'\$\$(\w+)\$\$')


def envrepl(match):
    name = match.group(1)
    val = os.environ.get(name, '')
    return val
