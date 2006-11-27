from durus.file_storage import FileStorage
from durus.connection import Connection
from shove import BaseStore

__all__ = ['DurusStore']


class DurusStore(BaseStore):

    def __init__(self, engine, **kw):
        super(DurusStore, self).__init__(engine, **kw)
        db = engine.split('/', 2)
        self._db = FileStorage(db)
        self._connection = Connection(self._db)
        self._store = self._connection.get_root() 

    def __setitem__(self, key, value):        
        self._store[key] = value
        self._connection.commit()

    def __delitem__(self, key):
        del self._store[key]
        self._connection.commit()

    def close(self):
        self._connection.commit()
        self._db.close()