#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
setup for shove.
'''

from setuptools import setup, find_packages

setup(
    name='shove',
    version='0.5.1',
    description='''Common object storage frontend''',
    long_description=open('README.rst').read(),
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='https://bitbucket.org/lcrees/shove/',
    license='BSD',
    packages=find_packages(),
    test_suite='shove.tests',
    install_requires=['futures', 'stuf>=0.8.19'],
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points='''
    [shove.stores]
    bsddb=shove.stores.bsdb:BSDBStore
    cassandra=shove.stores.cassandra:CassandraStore
    dbm=shove.store:DBMStore
    durus=shove.stores.durusdb:DurusStore
    file=shove.store:FileStore
    firebird=shove.stores.db:DBStore
    ftp=shove.stores.ftp:FTPStore
    hdf5=shove.stores.hdf5:HDF5Store
    leveldb=shove.stores.leveldbstore:LevelDBStore
    memory=shove.store:MemoryStore
    mongodb=shove.stores.mongodb:MongoDBStore
    mssql=shove.store.db:DBStore
    mysql=shove.stores.db:DBStore
    oracle=shove.stores.db:DBStore
    postgres=shove.store.db:DBStore
    redis=shove.stores.redisdb:RedisStore
    s3=shove.stores.s3:S3Store
    simple=shove.store:SimpleStore
    sqlite=shove.stores.db:DBStore
    zodb=shove.stores.zodb:ZODBStore
    hg=shove.stores.hgstore:HgStore
    git=shove.stores.gitstore:GitStore
    [shove.caches]
    file=shove.cache:FileCache
    filelru=shove.cache:FileLRUCache
    firebird=shove.caches.db:DBCache
    memcache=shove.caches.memcached:MemCache
    memlru=shove.cache:MemoryLRUCache
    memory=shove.caches:MemoryCache
    mssql=shove.caches.db:DBCache
    mysql=shove.caches.db:DBCache
    oracle=shove.caches.db:DBCache
    postgres=shove.caches.db:DBCache
    redis=shove.caches.redisdb:RedisCache
    simple=shove.cache:SimpleCache
    simplelru=shove.cache:SimpleLRUCache
    sqlite=shove.caches.db:DBCache
    ''',
)
