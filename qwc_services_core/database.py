import os

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class DatabaseEngine():
    """Helper for database connections using SQLAlchemy engines"""

    def __init__(self):
        """Constructor"""
        self.engines = {}

    def db_engine(self, conn_str, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=-1):
        """Return engine.

        :param str conn_str: DB connection string for SQLAlchemy engine
        :param int pool_size: Maximum number of possible connections
        :param int max_overflow: Additional connections beyond pool_size during peak load
        :param int pool_timeout: Time (in seconds) to wait for a connection to become available
        :param int pool_recycle: Time (in seconds) after idle connections will be resetted

        see https://docs.sqlalchemy.org/en/latest/core/engines.html#postgresql
        """

        db_pool_size = self.db_engine_env('POOL_SIZE', pool_size)
        db_max_overflow = self.db_engine_env('MAX_OVERFLOW', max_overflow)
        db_pool_timeout = self.db_engine_env('POOL_TIMEOUT', pool_timeout)
        db_pool_recycle = self.db_engine_env('POOL_RECYCLE', pool_recycle)

        engine = self.engines.get(conn_str)
        if not engine:
            engine = create_engine(
                conn_str, 
                poolclass=QueuePool,
                pool_size=db_pool_size,
                max_overflow=db_max_overflow, 
                pool_timeout=db_pool_timeout,
                pool_recycle=db_pool_recycle,
                pool_pre_ping=True, echo=False)
            self.engines[conn_str] = engine
        return engine

    def db_engine_env(self, env_name, default=None):
        """Return engine configured in environment variable.

        :param str env_name: Environment variable
        :param str default: Default value if environment variable is not set
        """
        env_value = os.environ.get(env_name, default)
        if env_value is None:
            raise Exception(
                'db_engine_env: Environment variable %s not set' % env_name)
        return self.db_engine(env_value)

    def geo_db(self):
        """Return engine for default GeoDB."""
        return self.db_engine_env('GEODB_URL',
                                  'postgresql:///?service=qwc_geodb')

    def config_db(self):
        """Return engine for default ConfigDB."""
        return self.db_engine_env('CONFIGDB_URL',
                                  'postgresql:///?service=qwc_configdb')
