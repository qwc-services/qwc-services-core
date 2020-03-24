from datetime import datetime
import os
import re
from flask import request

from .permissions_reader import PermissionsReader
from .runtime_config import RuntimeConfig


class TenantHandler:
    """Tenant handling class
    """

    def __init__(self, logger):
        """Constructor

        :param Logger logger: Application logger
        """
        self.logger = logger
        self.tenant_name = os.environ.get('QWC_TENANT')
        self.tenant_re = os.environ.get('TENANT_REFERRER_RE')
        if self.tenant_re:
            self.tenant_re = re.compile(self.tenant_re)
        self.handler_cache = {}  # handler_cache[handler_name][tenant]

    def tenant(self, identity):
        # TODO: support tenant in identity
        if self.tenant_name:
            return self.tenant_name
        if self.tenant_re and request.referrer:
            # Extract from referrer URL
            match = self.tenant_re.match(request.referrer)
            if match:
                return match.group(1)
        return 'default'

    def handler(self, service_name, handler_name, tenant):
        """Get service handler for tenant.

        Return None if not yet registered or if config files have changed.

        :param str service_name: Service name
                                 (used for detecting config changes)
        :param str handler_name: Handler name
        :param str tenant: Tenant ID
        """
        handlers = self.handler_cache.get(handler_name)
        if handlers:
            handler = handlers.get(tenant)
            if handler:
                # check for config updates
                last_update = self.last_config_update(service_name, tenant)
                if last_update and last_update < handler.get('last_update'):
                    # cache is up-to-date
                    return handler.get('handler')
                else:
                    # config has changed, remove handler from cache
                    del handlers[tenant]

        return None

    def register_handler(self, handler_name, tenant, handler):
        """Register service handler for tenant"""
        handlers = self.handler_cache.get(handler_name)
        if handlers is None:
            handlers = {}
            self.handler_cache[handler_name] = handlers
        handlers[tenant] = {
            'handler': handler,
            'last_update': datetime.utcnow()
        }
        return handler

    def last_config_update(self, service_name, tenant):
        """Return latest timestamp of config and permission files for a tenant.

        :param str service_name: Service name
        :param str tenant: Tenant ID
        """
        # get latest timestamp of config and permission files
        last_config_update = None
        paths = [
            RuntimeConfig.config_file_path(service_name, tenant),
            PermissionsReader.permissions_file_path(tenant)
        ]
        for path in paths:
            if os.path.isfile(path):
                timestamp = datetime.utcfromtimestamp(
                    os.path.getmtime(path)
                )
                if (
                    last_config_update is None
                    or timestamp > last_config_update
                ):
                    last_config_update = timestamp

        return last_config_update
