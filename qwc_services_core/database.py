import os

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class DatabaseEngine():
    """Helper for database connections using SQLAlchemy engines"""

    def __init__(self):
        """Constructor"""
        self.engines = {}

    def db_engine(self, conn_str, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=300):
        """Return engine.

        :param str conn_str: DB connection string for SQLAlchemy engine

        see https://docs.sqlalchemy.org/en/latest/core/engines.html#postgresql
        """
        engine = self.engines.get(conn_str)
        if not engine:
            engine = create_engine(
                conn_str, 
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow, 
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                pool_pre_ping=True, echo=False)
            self.engines[conn_str] = engine
        return engine

    def db_engine_env(self, env_name, default=None):
        """Return engine configured in environment variable.

        :param str env_name: Environment variable
        :param str default: Default value if environment variable is not set
        """
        conn_str = os.environ.get(env_name, default)
        if conn_str is None:
            raise Exception(
                'db_engine_env: Environment variable %s not set' % env_name)
        return self.db_engine(conn_str)

    def geo_db(self):
        """Return engine for default GeoDB."""
        return self.db_engine_env('GEODB_URL',
                                  'postgresql:///?service=qwc_geodb')

    def config_db(self):
        """Return engine for default ConfigDB."""
        return self.db_engine_env('CONFIGDB_URL',
                                  'postgresql:///?service=qwc_configdb')
