from datetime import datetime
import os
import time

import requests

from .cache import Cache


class PermissionClient():
    """PermissionClient class

    Get service specific permissions from permission service.
    """

    def __init__(self):
        """Constructor"""
        # get permission service URL from ENV (default: local service)
        self.service_url = os.environ.get(
            'CONFIG_SERVICE_URL', 'http://localhost:5010/').rstrip('/') + '/'
        # check if cache is valid every x seconds (default: 60s)
        self.config_check_interval = os.environ.get(
            'CONFIG_CHECK_INTERVAL', 60)
        # time in seconds until cache expiry (default: 24h)
        self.default_cache_duration = os.environ.get(
            'DEFAULT_CONFIG_CACHE_DURATION', 86400)

        self.headers = {
            'accept': 'application/json'
        }

        self.cache = Cache()
        self.last_update_check = None
        self.last_cache_flush = None

    def resource_permissions(self, resource_type, identity,
                             name=None, parent_id=None):
        """Return permitted resources for a resource type.

        :param str resource_type: Resource type
        :param obj identity: User name or Identity dict
        :param str name: Optional name filter
        :param str parent_id: Optional parent_id filter
        """
        params = {
            'resource_type': resource_type,
            'name': name,
            'parent_id': parent_id
        }
        return self.query_permissions(
            'resource_permissions', 'permissions/%s' % resource_type, params,
            identity, self.default_cache_duration, convert_int_keys=True
        )

    def resource_restrictions(self, resource_type, identity,
                              name=None, parent_id=None):
        """Return restricted resources for a resource type.

        :param str resource_type: Resource type
        :param obj identity: User name or Identity dict
        :param str name: Optional name filter
        :param str parent_id: Optional parent_id filter
        """
        params = {
            'resource_type': resource_type,
            'name': name,
            'parent_id': parent_id
        }
        return self.query_permissions(
            'resource_restrictions', 'restrictions/%s' % resource_type, params,
            identity, self.default_cache_duration, 'restrictions', True
        )

    def query_permissions(self, cache_key, path, params, identity,
                          cache_duration=86400, response_key='permissions',
                          convert_int_keys=False):
        """Return permissions or restrictions for a service or resource type.

        :param str cache_key: Key for cache lookup
        :param str path: Path for permissions ervice request
        :param obj params: Query specific request parameters
        :param obj identity: User name or Identity dict
        :param int cache_duration: Time in seconds until expiry (default: 24h)
        :param str response_key: Permissions key in JSON response
                                 (default: 'permissions')
        :paras bool convert_int_keys: Convert JSON integer keys to int
        """
        permissions = None
        if cache_duration:  # Caching active
            # check if cache is still valid
            self.check_cache()

            # get permissions from cache
            permissions = self.cache.read(
                cache_key, identity, params.values())
            if permissions:
                return permissions

        # build request URL: http://<service_url>/<path>
        url = self.service_url + path

        reqparams = params.copy()  # don't change params before cache.write
        if identity:
            if isinstance(identity, dict):
                reqparams.update({
                    'username': identity.get('username'),
                    'group': identity.get('group')
                })
            else:
                # identity is username
                reqparams.update({'username': identity})

        # send request to permission service
        response = requests.get(url, headers=self.headers, params=reqparams,
                                timeout=30)
        if response.status_code == requests.codes.ok:
            if convert_int_keys:
                permissions = {}
                result = response.json()[response_key]
                for key, value in result.items():
                    # convert integer keys from JSON from string to int
                    try:
                        key = int(key)
                    except ValueError:
                        pass
                    permissions[key] = value
            else:
                permissions = response.json()[response_key]

        if cache_duration:  # Caching active
            self.cache.write(cache_key, identity, params.values(),
                             permissions, cache_duration)

        return permissions

    def dataset_edit_permissions(self, dataset, identity):
        """Return dataset edit permissions if available and permitted.

        :param str dataset: Dataset ID
        :param obj identity: User name or Identity dict
        """
        return self.query_permissions(
            'data', 'data', {'dataset': dataset}, identity,
            self.default_cache_duration
        )

    def document_permissions(self, template, identity):
        """Return document template permissions if available and permitted.

        :param str dataset: Template ID
        :param obj identity: User name or Identity dict
        """
        return self.query_permissions(
            'document', 'document', {'template': template}, identity,
            self.default_cache_duration
        )

    def feature_info_permissions(self, ows_name, identity):
        """Return feature info template permissions if available and permitted.

        :param str ows_name: WMS service name
        :param obj identity: User name or Identity dict
        """
        return self.query_permissions(
            'feature_info', 'feature_info', {'ows_name': ows_name}, identity,
            self.default_cache_duration
        )

    def ogc_permissions(self, ows_name, ows_type, identity):
        """Return OGC service permissions if available and permitted.

        :param str ows_name: OWS service name
        :param str ows_type: OWS type (WMS or WFS)
        :param obj identity: User name or Identity dict
        """
        return self.query_permissions(
            'ogc', 'ogc', {'ows_name': ows_name, 'ows_type': ows_type},
            identity, self.default_cache_duration
        )

    def print_permissions(self, template, identity):
        """Return print template permissions if available and permitted.

        :param str dataset: Template ID
        :param obj identity: User name or Identity dict
        """
        return self.query_permissions(
            'print', 'print', {'template': template}, identity,
            self.default_cache_duration
        )

    def qwc_permissions(self, identity, viewer=None):
        """Return data for QWC themes.json for available and permitted
        resources.

        :param obj identity: User name or Identity dict
        :param str viewer: Optional custom viewer name (None for default)
        """
        return self.query_permissions(
            'qwc', 'qwc', {'viewer': viewer}, identity,
            self.default_cache_duration
        )

    def dataset_search_permissions(self, dataset, identity):
        """Return dataset search permissions if available and permitted.

        :param str dataset: Dataset ID
        :param obj identity: User name or Identity dict
        """
        return self.query_permissions(
            'search', 'search', {'dataset': dataset}, identity,
            self.default_cache_duration
        )

    def check_cache(self):
        """Check if cache is still valid and flush if obsolete."""
        if (self.last_update_check is None
            or self.last_update_check +
                self.config_check_interval < time.time()):
            # get last permissions update from permission service
            url = self.service_url + 'last_update'
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == requests.codes.ok:
                permissions_updated_at = datetime.strptime(
                    response.json()['permissions_updated_at'],
                    "%Y-%m-%d %H:%M:%S"
                )
                if (self.last_cache_flush is None
                        or self.last_cache_flush < permissions_updated_at):
                    # flush cache if obsolete
                    self.cache.init()
                    self.last_cache_flush = permissions_updated_at

            self.last_update_check = time.time()
