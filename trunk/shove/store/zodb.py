from ZODB import FileStorage, DB
import transaction
from shove.simple import SimpleStore

__all__ = ['ZodbStore']


class ZodbStore(BaseStore):

    def __init__(self, engine, **kw):
        super(ZodbStore, self).__init__(engine, **kw)
        db = engine.split('/', 2)
        self._storage = FileStorage.FileStorage(db)
        self._db = DB(self._storage)
        self._connection = self._db.open()
        self._store = self._connection.root()

    def __setitem__(self, key, value):        
        self._store[key] = value
        transaction.commit()

    def __delitem__(self, key):
        del self._store[key]
        transaction.commit()

    def close(self):
        transaction.commit()
        self._connection.close()
        self._db.close()
        self._storage.close()
        