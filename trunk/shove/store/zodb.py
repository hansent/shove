from ZODB import FileStorage, DB
import transaction
from shove import BaseStore


class ZodbStore(BaseStore):

    def __init__(self, engine, **kw):
        db = engine.split('/', 2)
        self._storage = FileStorage.FileStorage(db)
        self._db = DB(storage)
        self._connection = db.open()
        self._store = connection.root()

    def __getitem__(self, key):
        return pickle.loads(self._store[key])

    def __setitem__(self, key, value):        
        self._store[key] = pickle.dumps(value)
        transaction.commit()

    def __delitem__(self, key):
        del self._store[key]
        transaction.commit()

    def close(self):
        transaction.commit()
        self._connection.close()
        self._db.close()
        self._storage.close()
        