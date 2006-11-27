from ZODB import FileStorage, DB
import transaction
from shove.store import SyncStore

__all__ = ['ZodbStore']


class ZodbStore(SimpleStore):

    def __init__(self, engine, **kw):
        super(ZodbStore, self).__init__(engine, **kw)
        self.sync = transaction.commit
        self._storage = FileStorage.FileStorage(engine.split('/', 2))
        self._db = DB(self._storage)
        self._connection = self._db.open()
        self._store = self._connection.root()

    def close(self):
        self.sync()
        self._connection.close()
        self._db.close()
        self._storage.close()
        super(ZodbStore, self).close()
        