from boto.connection import S3Connection
from boto.key import Key
from shove import BaseStore
try:
    import cPickle as pickle
except ImportError:
    import pickle

class S3Store(BaseStore):    

    def __init__(self, engine=None, **kw):
        self._updated, self._keys = True, None
        ken, secret, bucket = kw.get('key'), kw.get('secret'), kw.get('bucket')
        if engine is not None:
            keys, bucket = engine.split('/', 2)[2].split('@')
            key, secret = keys.split(':')        
        self._conn = S3Connection(key, secret, kw.get('secure', False))
        buckets = self._conn.get_all_buckets()
        for b in buckets:
            if b.name == bucket: 
                self._store = b
                break
        else:
            self._store = self._conn.create_bucket(bucket)
            self._store.set_acl(kw.get('acl', 'private'))
    
    def __getitem__(self, key):
        rkey = self._store.lookup(key)
        if rkey is None: raise KeyError()
        self._updated = False
        return pickle.loads(rkey.get_contents_as_string())        

    def __setitem__(self, key, value):
        rkey = Key(self._store)
        rkey.key = key
        rkey.set_contents_from_string(pickle.dumps(value))
        self._updated = True

    def __delitem__(self, key):
        self._store.delete_key(key)
        self._updated = True

    def keys(self):
        if self._updated or self._keys is None:
            self._keys = self._store.get_all_keys()
        keys = self._keys
        return list(str(i.key) for i in keys)

    def iteritems(self):
        if self._updated or self._keys is None:
            self._keys = self._store.get_all_keys()
        keys = self._keys
        for k in keys: yield (k.key, k)

    def get_many(self, keys):
        if self._updated or self._keys is None:
            self._keys = self._store.get_all_keys()
        allkeys = self._keys()
        keyset = set(str(i.key) for i in allkeys)
        return dict((k.name, k) for k in allkeys if (k in keyset and k in keys)) 