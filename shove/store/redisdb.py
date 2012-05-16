# -*- coding: utf-8 -*-
'''
Redis-based object store

The shove URI for a redis-based store is:

redis://<host>:<port>/<db>
'''

try:
    import redis
except ImportError:
    raise ImportError('requires the redis library')

from shove._compat import urlsplit

from shove.store.core import ClientStore

__all__ = ['RedisStore']


class RedisStore(ClientStore):

    '''
    Redis based store.
    '''

    init = 'redis://'

    def __init__(self, engine, **kw):
        super(RedisStore, self).__init__(engine, **kw)
        spliturl = urlsplit(engine)
        db = spliturl.path.replace('/', '')
        self._store = redis.Redis(spliturl.hostname, spliturl.port, db)

    def __contains__(self, key):
        return self._store.exists(key)

    def clear(self):
        self._store.flushdb()

    def keys(self):
        return self._store.keys()

    def setdefault(self, key, default=None):
        return self._store.getset(key, default)

    def update(self, other=None, **kw):
        self._store.mset(kw if other is not None else other)
