import os
import re
from flask import request


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

    def handler(self, handler_name, tenant):
        """Get service handler for tenant"""
        handlers = self.handler_cache.get(handler_name)
        if handlers:
            return handlers.get(tenant)
        return None

    def register_handler(self, handler_name, tenant, handler):
        """Register service handler for tenant"""
        handlers = self.handler_cache.get(handler_name)
        if handlers is None:
            handlers = {}
            self.handler_cache[handler_name] = handlers
        handlers[tenant] = handler
        return handler
