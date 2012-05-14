# -*- coding: utf-8 -*-
'''setup - setuptools based setup for shove.'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='shove',
    version='0.5.0',
    description='''Common object storage frontend''',
    long_description=open('README.rst').read(),
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='https://bitbucket.org/lcrees/shove/',
    license='BSD',
    packages=['shove', 'shove.cache', 'shove.store', 'shove.tests'],
    py_modules=['ez_setup'],
    test_suite='shove.tests',
    zip_safe=False,
    keywords='object storage persistence database shelve',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points='''
    [shove.stores]
    bsddb=shove.store.bsdb:BsdStore
    cassandra=shove.store.cassandra:CassandraStore
    dbm=shove.store.core:DBMStore
    durus=shove.store.durusdb:DurusStore
    file=shove.store.core:FileStore
    firebird=shove.store.db:DBStore
    ftp=shove.store.ftp:FTPStore
    hdf5=shove.store.hdf5:HDF5Store
    leveldb=shove.store.leveldbstore:LevelDBStore
    memory=shove.store.core:MemoryStore
    mssql=shove.store.db:DBStore
    mysql=shove.store.db:DBStore
    oracle=shove.store.db:DBStore
    postgres=shove.store.db:DBStore
    redis=shove.store.redisdb:RedisStore
    s3=shove.store.s3:S3Store
    simple=shove.store.core:SimpleStore
    sqlite=shove.store.db:DBStore
    zodb=shove.store.zodb:ZODBStore
    [shove.caches]
    file=shove.cache.core:FileCache
    filelru=shove.cache.core:FileLRUCache
    firebird=shove.cache.db:DBCache
    memcache=shove.cache.memcached:MemCached
    memlru=shove.cache.core:MemoryLRUCache
    memory=shove.cache.core:MemoryCache
    mssql=shove.cache.db:DBCache
    mysql=shove.cache.db:DBCache
    oracle=shove.cache.db:DBCache
    postgres=shove.cache.db:DBCache
    redis=shove.cache.redisdb:RedisCache
    simple=shove.cache.core:SimpleCache
    simplelru=shove.cache.core:SimpleLRUCache
    sqlite=shove.cache.db:DBCache
    '''
)
