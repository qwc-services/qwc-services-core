import os
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
        self.service_url = os.environ.get('CONFIG_SERVICE_URL',
                                          'http://localhost:5010/')
        self.headers = {
            'accept': 'application/json'
        }
        self.cache = Cache()

    def service_permissions(self, service, params, username,
                            cache_duration=300):
        """Return service permissions if available and permitted.

        :param str service: Service type
        :param obj params: Service specific request parameters
        :param str username: User name
        :param int cache_duration: Time in seconds until expiry (default: 300s)
        """
        permissions = None
        if cache_duration:  # Caching active
            # TODO: Check if cache still valid
            # If last request > 1' request to permssion service
            # self.cache.init() if not valid
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
            'data', {'dataset': dataset}, username
        )

    def document_permissions(self, template, username):
        """Return document template permissions if available and permitted.

        :param str dataset: Template ID
        :param str username: User name
        """
        return self.service_permissions(
            'document', {'template': template}, username
        )

    def feature_info_permissions(self, ows_name, username):
        """Return feature info template permissions if available and permitted.

        :param str ows_name: WMS service name
        :param str username: User name
        """
        return self.service_permissions(
            'feature_info', {'ows_name': ows_name}, username
        )

    def ogc_permissions(self, ows_name, ows_type, username):
        """Return OGC service permissions if available and permitted.

        :param str ows_name: OWS service name
        :param str ows_type: OWS type (WMS or WFS)
        :param str username: User name
        """
        return self.service_permissions(
            'ogc', {'ows_name': ows_name, 'ows_type': ows_type}, username
        )

    def print_permissions(self, template, username):
        """Return print template permissions if available and permitted.

        :param str dataset: Template ID
        :param str username: User name
        """
        return self.service_permissions(
            'print', {'template': template}, username
        )

    def qwc_permissions(self, username):
        """Return data for QWC themes.json for available and permitted resources.

        :param str username: User name
        """
        return self.service_permissions(
            'qwc', {}, username, cache_duration=300  # TODO: 10*3600
        )

    def dataset_search_permissions(self, dataset, username):
        """Return dataset search permissions if available and permitted.

        :param str dataset: Dataset ID
        :param str username: User name
        """
        return self.service_permissions(
            'search', {'dataset': dataset}, username
        )
