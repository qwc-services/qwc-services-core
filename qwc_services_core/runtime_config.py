import os
import re
from flask import json, safe_join


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

    def __init__(self, service, logger):
        self.service = service
        self.logger = logger
        self.config = None

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
            if val is None:
                # unkown type --> no conversion
                val = envval
            elif type(val) in (list, dict):
                val = json.loads(envval)
            else:
                val = type(val)(envval)

        return val

    def resources(self):
        return self.config.get('resources')

    def resource(self, name):
        return self.config.get('resources', {}).get(name)


ENVVAR_PATTERN = re.compile(r'{{(\w+)}}')


def envrepl(match):
    name = match.group(1)
    val = os.environ.get(name, '')
    return val
