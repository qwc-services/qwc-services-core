import os

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class DatabaseEngine():
    """Helper for database connections using SQLAlchemy engines"""

    def __init__(self):
        """Constructor"""
        self.engines = {}

    def db_engine(self, conn_str):
        """Return engine.

        :param str conn_str: DB connection string for SQLAlchemy engine

        see https://docs.sqlalchemy.org/en/latest/core/engines.html#postgresql
        """

        db_pool_size = os.environ.get('POOL_SIZE', 5)
        db_max_overflow = os.environ.get('MAX_OVERFLOW', 10)
        db_pool_timeout = os.environ.get('POOL_TIMEOUT', 30)
        db_pool_recycle = os.environ.get('POOL_RECYCLE', -1)

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
