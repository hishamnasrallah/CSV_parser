from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from core.settings.base import settings

READ_WRITE = 'read_write'
READ = 'read'
TEST_DB = 'test'


class _DBPool:
    def __init__(self, name, url, pool_size=100, max_overflow=10):
        self.name = name
        self.url = url
        self.engine = create_engine(url, pool_size=pool_size, max_overflow=10)
        self.session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        return


# global handle for the DB session, it is a callable object,
# once called, it will create a new background session.
pools = {READ: _DBPool(READ, settings.db_url),
         READ_WRITE: _DBPool(READ_WRITE, settings.db_url),
         TEST_DB: _DBPool(TEST_DB, settings.db_url)}


class DBSession:
    """Example Usage with DBSession() as database: do sth """
    """Example 2 Usage with DBSession(READ) as database: do sth """

    def __init__(self, pool_name=READ_WRITE):
        self.pool = pools.get(pool_name, READ_WRITE)

    def __enter__(self):
        self.db = self.pool.session
        # constructs a new session by calling database()
        self.db()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__close()

    def __close(self):
        self.db.remove()
