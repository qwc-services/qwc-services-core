"""Authentication helper functions
"""
import os
import re
from flask import request
from .jwt import jwt_manager
from flask_jwt_extended import jwt_required, get_jwt_identity


# Accept user name passed in Basic Auth header
# (password has to checkded before!)
ALLOW_BASIC_AUTH_USER = os.environ.get('ALLOW_BASIC_AUTH_USER', 'False') \
    .lower() in ('t', 'true')


def auth_manager(app, api=None):
    """Authentication setup for Flask app"""
    # Setup the Flask-JWT-Extended extension
    return jwt_manager(app, api)


def optional_auth(fn):
    """Authentication view decorator"""
    return jwt_required(optional=True)(fn)


def get_identity():
    """Get identity (username or dict with username and groups)
       or optional pre-authenticated basic auth user"""
    identity = get_jwt_identity()
    if not identity and ALLOW_BASIC_AUTH_USER:
        auth = request.authorization
        if auth:
            # We don't check password, already authenticated!
            identity = auth.username
    return identity


def get_username(identity):
    """Extract username from identity"""
    username = None
    if identity:
        if isinstance(identity, dict):
            username = identity.get('username')
        else:
            # identity is username
            username = identity
    return username


def get_groups(identity):
    """Extract user groups from identity"""
    groups = []
    if identity:
        if isinstance(identity, dict):
            groups = identity.get('groups', [])
            group = identity.get('group')
            if group:
                groups.append(group)
    return groups


class GroupNameMapper:
    """Group name mapping with regular expressions"""

    def __init__(self, default=''):
        group_mappings = os.environ.get('GROUP_MAPPINGS', default)

        def collect(mapping):
            regex, *replacement = mapping.split('~', 1)
            return (re.compile(regex), replacement[0])

        self.group_mappings = list(
            map(collect, group_mappings.split('#'))) if group_mappings else []

    def mapped_group(self, group):
        # LDAP servers my return a group as list object
        if isinstance(group, list):
            group = ' '.join(group)
        for (regex, replacement) in self.group_mappings:
            if regex.match(group):
                return regex.sub(replacement, group)
        return group

# Usage examples:
# mapper = GroupNameMapper('ship_crew~crew#gis.role.(.*)~\\1')
# print(mapper.mapped_group('ship_crew'))
# print(mapper.mapped_group('gis.role.admin'))
# print(mapper.mapped_group('gis.role.user.group1'))
# print(mapper.mapped_group('gis.none'))
