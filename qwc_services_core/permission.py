from datetime import datetime
import os
import time
from urllib.parse import urljoin

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

    def resource_permissions(self, resource_type, params, username,
                             cache_duration=86400):
        """Return permitted resources for a resource type.

        :param str resource_type: Resource type
        :param obj params: Optional request parameters with
                           name=<name filter>&parent_id=<parent filter>
        :param str username: User name
        :param int cache_duration: Time in seconds until expiry (default: 24h)
        """
        permissions = None

        cache_key = "permitted_%s" % resource_type

        if cache_duration:  # Caching active
            # check if cache is still valid
            self.check_cache()

            # get permissions from cache
            permissions = self.cache.read(
                cache_key, username, params.values())
            if permissions:
                return permissions

        # build request URL: http://<service_url>/permissions/<resource_type>
        url = urljoin(self.service_url, 'permissions/%s' % resource_type)

        reqparams = params.copy()  # don't change params before cache.write
        if username:
            reqparams.update({'username': username})

        # send request to permission service
        response = requests.get(url, headers=self.headers, params=reqparams,
                                timeout=30)
        if response.status_code == requests.codes.ok:
            permissions = response.json()['permissions']

        if cache_duration:  # Caching active
            self.cache.write(cache_key, username, params.values(),
                             permissions, cache_duration)

        return permissions

    def resource_restrictions(self, resource_type, params, username,
                              cache_duration=86400):
        """Return restricted resources for a resource type.

        :param str resource_type: Resource type
        :param obj params: Optional request parameters with
                           name=<name filter>&parent_id=<parent filter>
        :param str username: User name
        :param int cache_duration: Time in seconds until expiry (default: 24h)
        """
        restrictions = None

        cache_key = "restricted_%s" % resource_type

        if cache_duration:  # Caching active
            # check if cache is still valid
            self.check_cache()

            # get restrictions from cache
            restrictions = self.cache.read(
                cache_key, username, params.values())
            if restrictions:
                return restrictions

        # build request URL: http://<service_url>/restrictions/<resource_type>
        url = urljoin(self.service_url, 'restrictions/%s' % resource_type)

        reqparams = params.copy()  # don't change params before cache.write
        if username:
            reqparams.update({'username': username})

        # send request to permission service
        response = requests.get(url, headers=self.headers, params=reqparams,
                                timeout=30)
        if response.status_code == requests.codes.ok:
            restrictions = response.json()['restrictions']

        if cache_duration:  # Caching active
            self.cache.write(cache_key, username, params.values(),
                             restrictions, cache_duration)

        return restrictions

    def service_permissions(self, service, params, username,
                            cache_duration=86400):
        """Return service permissions if available and permitted.

        :param str service: Service type
        :param obj params: Service specific request parameters
        :param str username: User name
        :param int cache_duration: Time in seconds until expiry (default: 24h)
        """
        permissions = None
        if cache_duration:  # Caching active
            # check if cache is still valid
            self.check_cache()

            # get permissions from cache
            permissions = self.cache.read(
                service, username, params.values())
            if permissions:
                return permissions

        # build request URL: http://<service_url>/<service>
        url = urljoin(self.service_url, '%s' % service)

        reqparams = params.copy()  # don't change params before cache.write
        if username:
            reqparams.update({'username': username})

        # send request to permission service
        response = requests.get(url, headers=self.headers, params=reqparams,
                                timeout=30)
        if response.status_code == requests.codes.ok:
            permissions = response.json()['permissions']

        if cache_duration:  # Caching active
            self.cache.write(service, username, params.values(),
                             permissions, cache_duration)

        return permissions

    def dataset_edit_permissions(self, dataset, username):
        """Return dataset edit permissions if available and permitted.

        :param str dataset: Dataset ID
        :param str username: User name
        """
        return self.service_permissions(
            'data', {'dataset': dataset}, username, self.default_cache_duration
        )

    def document_permissions(self, template, username):
        """Return document template permissions if available and permitted.

        :param str dataset: Template ID
        :param str username: User name
        """
        return self.service_permissions(
            'document', {'template': template}, username,
            self.default_cache_duration
        )

    def feature_info_permissions(self, ows_name, username):
        """Return feature info template permissions if available and permitted.

        :param str ows_name: WMS service name
        :param str username: User name
        """
        return self.service_permissions(
            'feature_info', {'ows_name': ows_name}, username,
            self.default_cache_duration
        )

    def ogc_permissions(self, ows_name, ows_type, username):
        """Return OGC service permissions if available and permitted.

        :param str ows_name: OWS service name
        :param str ows_type: OWS type (WMS or WFS)
        :param str username: User name
        """
        return self.service_permissions(
            'ogc', {'ows_name': ows_name, 'ows_type': ows_type}, username,
            self.default_cache_duration
        )

    def print_permissions(self, template, username):
        """Return print template permissions if available and permitted.

        :param str dataset: Template ID
        :param str username: User name
        """
        return self.service_permissions(
            'print', {'template': template}, username,
            self.default_cache_duration
        )

    def qwc_permissions(self, username):
        """Return data for QWC themes.json for available and permitted
        resources.

        :param str username: User name
        """
        return self.service_permissions(
            'qwc', {}, username, self.default_cache_duration
        )

    def dataset_search_permissions(self, dataset, username):
        """Return dataset search permissions if available and permitted.

        :param str dataset: Dataset ID
        :param str username: User name
        """
        return self.service_permissions(
            'search', {'dataset': dataset}, username,
            self.default_cache_duration
        )

    def check_cache(self):
        """Check if cache is still valid and flush if obsolete."""
        if (self.last_update_check is None
            or self.last_update_check +
                self.config_check_interval < time.time()):
            # get last permissions update from permission service
            url = urljoin(self.service_url, 'last_update')
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
