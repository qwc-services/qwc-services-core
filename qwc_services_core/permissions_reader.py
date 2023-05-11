from copy import deepcopy
import os

from flask import json
from werkzeug.utils import safe_join
from .auth import get_username, get_groups


class PermissionsReader():
    """PermissionsReader helper class

    Read users, groups, roles and permissions for a tenant from a JSON file.
    Provides helper methods for collectiong permissions.
    """

    # name of public role
    PUBLIC_ROLE_NAME = 'public'

    @staticmethod
    def permissions_file_path(tenant):
        """Return path to permissions JSON file for a tenant.

        :param str tenant: Tenant ID
        """
        config_path = os.environ.get('CONFIG_PATH', 'config')
        return safe_join(config_path, tenant, 'permissions.json')

    def __init__(self, tenant, logger):
        """Constructor

        :param str tenant: Tenant ID
        :param Logger logger: Application logger
        """
        self.tenant = tenant
        self.logger = logger
        self.permissions = self.load_permissions()

    def read_permissions(self):
        """Read permissions for a tenant from a JSON file."""
        permissions = {}

        permissions_path = PermissionsReader.permissions_file_path(self.tenant)
        self.logger.info("Reading permissions '%s'" % permissions_path)
        try:
            with open(permissions_path, encoding='utf-8') as fh:
                permissions = json.load(fh)
        except Exception as e:
            self.logger.error(
                "Could not load permissions '%s':\n%s" %
                (permissions_path, e)
            )
            raise e
        # TODO: validate permissions schema

        return permissions

    def load_permissions(self):
        """Load users, groups, roles and permissions.

        Returns lookup dict as:
            {
                users: {
                    <user>: [<role>]
                }
                groups: {
                    <group>: [<role>]
                },
                roles: {
                    <role>: <permissions{}>
                }
            }
        """
        permissions = self.read_permissions()

        # transform raw permissions to lookup dict

        # detect permissions schema type
        is_unified = (
            'dataproducts' in permissions and 'common_resources' in permissions
        )

        resources_lookup = {}
        if is_unified:
            # create lookup for resources
            for resource in permissions.get('dataproducts', []):
                resources_lookup[resource.get('name')] = resource

        # collect group roles
        groups = {}
        for group in permissions.get('groups', []):
            groups[group['name']] = group['roles'] or []

        # collect user roles
        users = {}
        for user in permissions.get('users', []):
            user_roles = []
            # direct roles
            for role in user.get('roles', []) or []:
                user_roles.append(role)
            # roles from groups
            for group in user['groups'] or []:
                user_roles.extend(groups.get(group, []))
            # assign unique sorted roles
            users[user['name']] = sorted(list(set(user_roles)))

        # collect role permissions
        roles = {}
        for role in permissions.get('roles', []):
            if not is_unified:
                roles[role['role']] = role['permissions']
            else:
                roles[role['role']] = self.expand_unified_permissions(
                    role['permissions'], deepcopy(resources_lookup), permissions
                )

        return {
            'users': users,
            'groups': groups,
            'roles': roles
        }

    def expand_unified_permissions(self, role_permissions, resources_lookup,
                                   permissions):
        """Return full resource permissions expanded from unified permissions.

        :param obj role_permissions: Unified permissions for role
        :param obj resources_lookup: Lookup for resources with sublayers or
                                     attributes
        :param obj permissions: Permissions from JSON
        """
        full_permissions = {}

        wms_name = permissions.get('wms_name', '')
        wfs_name = permissions.get('wfs_name', '')
        # common resources for internal print layers, background layers,
        #   print templates and default solr facets
        common_resources = permissions.get('common_resources', [])

        wms_layers = []
        # add WMS root layer
        wms_layers.append({
            'name': wms_name
        })
        wfs_layers = []
        data_datasets = []
        dataproducts = []
        dataproducts.append(wms_name)
        document_templates = []
        solr_facets = []

        # convert all_services dict to resources list
        all_services = []
        for name, resource in role_permissions.get('all_services', {}).items():
            all_services.append({
                'name': name
            })
            # copy writable flags from all_services to resources_lookup
            if 'writable' in resource:
                lookup = resources_lookup.get(name, {})
                lookup['writable'] = resource['writable']

        # collect permitted resources for role
        role_resources = self.collect_resources(
            all_services, resources_lookup
        )

        # expand to full QWC service permissions
        # NOTE: This generates more permissions than there are actual resources
        #       in a specific service. Any surplus permissions will be ignored.
        for resource in role_resources:
            if 'attributes' in resource:
                # single layer

                # add default 'geometry' column to WMS/WFS attributes
                ogc_attributes = resource['attributes'] + ['geometry']

                # add potential WMS layer
                wms_layers.append({
                    'name': resource['name'],
                    'attributes': ogc_attributes,
                    # NOTE: any info templates are always permitted
                    'info_template': True
                })

                # add potential WFS layer
                wfs_layers.append({
                    'name': resource['name'],
                    'attributes': ogc_attributes
                })

                # add potential Data service dataset
                data_datasets.append({
                    'name': resource['name'],
                    # NOTE: attributes without geometry column
                    'attributes': resource['attributes'],
                    'writable': resource.get('writable', False),
                    # NOTE: always readable
                    'readable': True
                })

                # add potential Solr facet
                solr_facets.append(resource['name'])
            else:
                # add potential group layer to WMS
                wms_layers.append({
                    'name': resource['name']
                })

            dataproducts.append(resource['name'])

            if list(resource.keys()) == ['name']:
                # potential document template has no keys except 'name'
                document_templates.append(resource['name'])

        # add potential internal print layers to WMS
        wms_layers += [
            {'name': name} for name in common_resources
        ]

        # NOTE: assume single WMS service
        full_permissions['wms_services'] = [{
            'name': wms_name,
            'layers': wms_layers,
            # add potential print templates
            'print_templates': common_resources
        }]

        # NOTE: assume single WFS service
        full_permissions['wfs_services'] = [{
            'name': wfs_name,
            'layers': wfs_layers
        }]

        full_permissions['background_layers'] = common_resources
        full_permissions['data_datasets'] = data_datasets
        full_permissions['dataproducts'] = dataproducts
        full_permissions['document_templates'] = document_templates

        # add potential default Solr facets
        solr_facets += common_resources
        full_permissions['solr_facets'] = solr_facets

        return full_permissions

    def collect_resources(self, parent_resources, resources_lookup):
        """Recursively collect resources from 'all_services' and return
        flat list of permitted resources.

        :param list<obj> parent_resources: Parent resources
        :param obj resources_lookup: Lookup for resources with sublayers or
                                     attributes
        """
        resources = []

        for resource in parent_resources:
            # merge with any resource from lookup
            lookup = resources_lookup.get(resource['name'], {})
            resource.update(lookup)

            if 'processed' not in lookup:
                # add resource
                resources.append(resource)
                # mark lookup as processed to skip duplicates
                lookup['processed'] = True
            else:
                # skip duplicates
                continue

            if 'sublayers' in resource:
                # recursively collect sublayers
                sub_resources = [
                    {'name': name} for name in resource['sublayers']
                ]
                resources += self.collect_resources(
                    sub_resources, resources_lookup
                )

        return resources

    # helpers

    def identity_roles(self, identity):
        """Return roles for identity.

        :param obj identity: User identity
        """
        # extract username and group
        username = get_username(identity)
        groups = get_groups(identity)

        # add default public role
        roles = [self.PUBLIC_ROLE_NAME]
        # add any user roles
        roles.extend(self.permissions['users'].get(username, []))
        # add any group roles
        for group in groups:
            roles.extend(self.permissions['groups'].get(group, []))

        # return unique sorted roles
        return sorted(list(set(roles)))

    def resource_permissions(self, resource_key, identity, resource_name=None):
        """Return collected list of resource permissions for identity roles.

        :param str resource_key: Resource key in permissions data
        :param obj identity: User identity
        :param str name: Optional resource name filter
        """
        permissions = []

        roles = self.identity_roles(identity)
        for role in roles:
            # get role permissions
            role_permissions = self.permissions['roles'].get(role, {})
            # get permissions for resource key
            resource_permissions = role_permissions.get(resource_key, {})
            if resource_name is not None:
                # filter by resource name
                for permission in resource_permissions:
                    if isinstance(permission, dict):
                        if permission.get('name') == resource_name:
                            permissions.append(permission)
                    else:
                        if permission == resource_name:
                            permissions.append(permission)
            else:
                permissions.extend(resource_permissions)

        return permissions
