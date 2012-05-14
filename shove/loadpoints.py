# -*- coding: utf-8 -*-
'''shove loadpoints.'''
from stuf.utils import lazyimport

try:
    # import store and cache entry points if setuptools installed
    import pkg_resources
    stores = dict((_store.name, _store) for _store in
        pkg_resources.iter_entry_points('shove.stores'))
    caches = dict((_cache.name, _cache) for _cache in
        pkg_resources.iter_entry_points('shove.caches'))
    # pass if nothing loaded
    if not stores and not caches:
        raise ImportError()
except ImportError:
    # static store backend registry
    stores = dict(
        bsddb='shove.store.bsdb:BSDSBtore',
        cassandra='shove.store.cassandra:CassandraStore',
        dbm='shove.store.core:DBMStore',
        durus='shove.store.durusdb:DurusStore',
        file='shove.store.core:FileStore',
        firebird='shove.store.db:DBStore',
        ftp='shove.store.ftp:FTPStore',
        hdf5='shove.store.hdf5:HDF5Store',
        leveldb='shove.store.leveldbstore:LevelDBStore',
        memory='shove.store.core:MemoryStore',
        mssql='shove.store.db:DBStore',
        mysql='shove.store.db:DBStore',
        oracle='shove.store.db:DBStore',
        postgres='shove.store.db:DbStore',
        redis='shove.store.redisdb:RedisStore',
        s3='shove.store.s3:S3Store',
        simple='shove.store.core:SimpleStore',
        sqlite='shove.store.db:DBStore',
        zodb='shove.store.zodb:ZODBStore',
    )
    # static cache backend registry
    caches = dict(
        file='shove.cache.core:FileCache',
        filelru='shove.cache.core:FileLRUCache',
        firebird='shove.cache.db:DBCache',
        memcache='shove.cache.memcached:MemCached',
        memlru='shove.cache.core:MemoryLRUCache',
        memory='shove.cache.core:MemoryCache',
        mssql='shove.cache.db:DBCache',
        mysql='shove.cache.db:DBCache',
        oracle='shove.cache.db:DBCache',
        postgres='shove.cache.db:DBCache',
        redis='shove.cache.redisdb:RedisCache',
        simple='shove.cache.core:SimpleCache',
        simplelru='shove.cache.core:SimpleLRUCache',
        sqlite='shove.cache.db:DBCache',
    )


def cache_backend(uri, **kw):
    '''
    Loads the right cache backend based on a URI.

    :argument uri: instance or name :class:`str`
    '''
    if isinstance(uri, basestring):
        mod = caches[uri.split('://', 1)[0]]
        # load module if setuptools not present
        if isinstance(mod, basestring):
            # split classname from dot path
            module, klass = mod.split(':')
            # load module
            mod = getattr(__import__(module, '', '', ['']), klass)
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
    if isinstance(uri, basestring):
        mod = stores[uri.split('://', 1)[0]]
        # load module if setuptools not present
        if isinstance(mod, basestring):
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
