# -*- coding: utf-8 -*-
'''shove compatibility for different python versions'''

try:
    import unittest2 as unittest
except ImportError:
    import unittest
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
except:
    import dbm as anydbm

from stuf.six import strings, items, keys, PY3
from stuf.six.moves import StringIO, xrange as range, cPickle as pickle


def openit(path, mode, encoding='utf-8'):
    return open(path, mode, encoding=encoding) if PY3 else open(path, mode)
