import os
from flask import json, safe_join


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

        # collect group roles
        groups = {}
        for group in permissions.get('groups', []):
            groups[group['name']] = group['roles']

        # collect user roles
        users = {}
        for user in permissions.get('users', []):
            user_roles = []
            # direct roles
            for role in user['roles']:
                user_roles.append(role)
            # roles from groups
            for group in user['groups']:
                user_roles.extend(groups.get(group, []))
            # assign unique sorted roles
            users[user['name']] = sorted(list(set(user_roles)))

        # collect role permissions
        roles = {}
        for role in permissions.get('roles', []):
            roles[role['role']] = role['permissions']

        return {
            'users': users,
            'groups': groups,
            'roles': roles
        }

    # helpers

    def identity_roles(self, identity):
        """Return roles for identity.

        :param obj identity: User identity
        """
        # extract username and group
        username = None
        group = None
        groups = []
        if identity:
            if isinstance(identity, dict):
                username = identity.get('username')
                group = identity.get('group')
                groups = identity.get('groups', [])
            else:
                # identity is username
                username = identity
        if group:
            groups.append(group)

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
