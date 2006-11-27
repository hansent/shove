from durus.file_storage import FileStorage
from durus.connection import Connection
from shove.store import SyncStore

__all__ = ['DurusStore']


class DurusStore(SyncStore):

    def __init__(self, engine, **kw):
        super(DurusStore, self).__init__(engine, **kw)
        self._db = FileStorage(engine.split('/', 2))
        self._connection = Connection(self._db)
        self.sync = self._connection.commit
        self._store = self._connection.get_root() 

    def close(self):
        self.sync()
        self._db.close()
        super(DurusStore, self).close()