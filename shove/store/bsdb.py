# -*- coding: utf-8 -*-
'''
Berkeley Source Database Store.

shove's psuedo-URL for BSDDB stores follows the form:

bsddb://<path>

Where the path is a URL path to a Berkeley database. Alternatively, the native
pathname to a Berkeley database can be passed as the 'engine' parameter.
'''

from threading import Condition

try:
    import bsddb
except ImportError:
    raise ImportError('requires bsddb library')

from shove._compat import synchronized
from shove.store.core import SyncStore

__all__ = ['BSDBStore']


class BSDBStore(SyncStore):

    '''
    Berkeley Source Database store.
    '''

    init = 'bsddb://'

    def __init__(self, engine, **kw):
        super(BSDBStore, self).__init__(engine, **kw)
        self._store = bsddb.hashopen(self._engine)
        self._lock = Condition()
        self.sync = self._store.sync

    __getitem__ = synchronized(SyncStore.__getitem__)
    __setitem__ = synchronized(SyncStore.__setitem__)
    __delitem__ = synchronized(SyncStore.__delitem__)
