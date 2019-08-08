import time
import copy


class ExpiringDict:
    """Dict for values where each key will expire after some time."""

    def __init__(self):
        """Constructor"""
        self.cache = {}

    def set(self, key, value, duration=300):
        """Store value under key until expiry.

        :param str key: Key for value
        :param obj value: Value to store
        :param int duration: Time in seconds until expiry (default: 300s)
        """
        self.cache[key] = {
            'value': copy.deepcopy(value),
            'expires': time.time() + duration
        }

    def lookup(self, key):
        """Return dict with value or None if not present or expired.

        :param str key: Key for value

        Returns {'value': <value>} or None
        """
        res = None

        if key in self.cache:
            entry = self.cache[key]
            # check expiry
            if time.time() < entry['expires']:
                # return value
                res = {'value':  copy.deepcopy(entry['value'])}
            else:
                # remove expired value
                del self.cache[key]

        return res


class Cache():
    """Nested dict for values where each key will expire after some time."""

    def __init__(self):
        self.init()

    def init(self):
        self.cache = {}

    def identity_keys(self, identity):
        """Return [group, username] for identity.

        :param obj identity: User name or Identity dict
        """
        if identity is not None:
            if isinstance(identity, dict):
                return [
                    identity.get('group'),
                    identity.get('username')
                ]
            else:
                # identity is username
                return [None, identity]
        else:
            # keys for empty user
            return [None, '_public_']

    def cache_entry(self, service, identity, keys):
        # cache is a nested dict with the following levels:
        cache_keys = [service] + self.identity_keys(identity) + list(keys)
        # print("cache_entry %s" % cache_keys)
        cache = self.cache

        # read or initialize cache level by level
        for key in cache_keys[:-2]:
            entry = cache.get(key)
            if entry is None:
                entry = {}
                cache[key] = entry
            cache = entry

        # second last key points to ExpiringDict cache entry
        key = cache_keys[-2]
        entry = cache.get(key)
        if entry is None:
            entry = ExpiringDict()
            cache[key] = entry

        key = cache_keys[-1]
        return (entry, key)

    def read(self, service, identity, keys):
        cache, key = self.cache_entry(service, identity, keys)
        entry = cache.lookup(key)
        if entry:
            # print("Reading data from cache with key '%s'" % key)
            return entry['value']
        else:
            return None

    def write(self, service, identity, keys, data,
              cache_duration):
        cache, key = self.cache_entry(service, identity, keys)
        # print("Writing data into cache with key '%s'" % key)
        cache.set(key, data, cache_duration)
