# -*- coding: utf-8 -*-
'''shove compatibility for different python versions'''

try:
    from urlparse import urlsplit
    from urllib import quote_plus, unquote_plus
except ImportError:
    from urllib.parse import urlsplit, quote_plus, unquote_plus
try:
    from urllib import url2pathname
except ImportError:
    from urllib.request import url2pathname
try:
    import anydbm
except ImportError:
    import dbm as anydbm

from stuf.six import PY3
from stuf.six.moves import StringIO  # @UnresolvedImport


def synchronized(func):
    '''
    Decorator to lock and unlock a method (Phillip J. Eby).

    @param func Method to decorate
    '''
    def wrapper(self, *__args, **__kw):
        self._lock.acquire()
        try:
            return func(self, *__args, **__kw)
        finally:
            self._lock.release()
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper


def openit(path, mode, encoding='utf-8'):
    return open(path, mode, encoding=encoding) if PY3 else open(path, mode)
