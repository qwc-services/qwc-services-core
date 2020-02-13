import os
from flask import json, safe_join


class RuntimeConfig:
    '''Runtime configuration helper class
    '''

    def __init__(self, service, logger):
        self.service = service
        self.logger = logger
        self.config = None

    def read_config(self, tenant):
        config_path = os.environ.get('CONFIG_PATH', 'config')
        filename = '%sConfig.json' % self.service
        runtime_config_path = safe_join(config_path, tenant, filename)
        self.logger.info(
            "Reading runtime config '%s'" % runtime_config_path
        )
        try:
            with open(runtime_config_path, encoding='utf-8') as fh:
                self.config = json.load(fh)
        except Exception as e:
            self.logger.error(
                "Could not load runtime config '%s':\n%s" %
                (runtime_config_path, e)
            )
            raise e
        # TODO: validate config
        return self

    def tenant_config(self, tenant):
        return self.read_config(tenant)

    def get(self, name, default=None):
        val = os.environ.get(name.upper())
        if val is None:
            val = self.config['config'][name]
        if val is None:
            val = default
        return val

    def resources(self):
        return self.config['resources']

    def resource(self, name):
        return self.config['resources'][name]
