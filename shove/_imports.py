# -*- coding: utf-8 -*-
'''shove loadpoints.'''

from stuf.six import strings
from stuf.utils import lazyimport
from pkg_resources import iter_entry_points

stores = dict(
    (_store.name, _store) for _store in iter_entry_points('shove.stores')
)
caches = dict(
    (_cache.name, _cache) for _cache in iter_entry_points('shove.caches')
)


def cache_backend(uri, **kw):
    '''
    Loads the right cache backend based on a URI.

    :argument uri: instance or name :class:`str`
    '''
    if isinstance(uri, strings):
        mod = caches[uri.split('://', 1)[0]]
        # load module if setuptools not present
        if isinstance(mod, strings):
            # split classname from dot path
            module, klass = mod.split(':')
            # load module
            mod = lazyimport(module, klass)
        # load appropriate class from setuptools entry point
        else:
            mod = mod.load()
        # return instance
        return mod(uri, **kw)
    # no-op for existing instances
    return uri


def store_backend(uri, **kw):
    '''
    Loads the right store backend based on a URI.

    :argument uri: instance or name :class:`str`
    '''
    if isinstance(uri, strings):
        mod = stores[uri.split('://', 1)[0]]
        # load module if setuptools not present
        if isinstance(mod, strings):
            # isolate classname from dot path
            module, klass = mod.split(':')
            # load module
            mod = lazyimport(module, klass)
        # load appropriate class from setuptools entry point
        else:
            mod = mod.load()
        # return instance
        return mod(uri, **kw)
    # no-op for existing instances
    return uri
