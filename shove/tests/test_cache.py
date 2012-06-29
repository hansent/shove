# -*- coding: utf-8 -*-
'''shove cache tests'''

from stuf.six import PY3, unittest
from shove.tests.mixins import Spawn

setUpModule = Spawn.setUpModule
tearDownModule = Spawn.tearDownModule


class NoTimeout(object):

    def setUp(self):
        self.cache = self._makeone(self.initstring)

    def tearDown(self):
        self.cache = None

    def test_getitem(self):
        self.cache['test'] = 'test'
        self.assertEqual(self.cache['test'], 'test')

    def test_setitem(self):
        self.cache['test'] = 'test'
        self.assertEqual(self.cache['test'], 'test')

    def test_delitem(self):
        self.cache['test'] = 'test'
        del self.cache['test']
        self.assertEqual('test' in self.cache, False)


class Cache(NoTimeout):

    def test_timeout(self):
        import time
        cache = self._makeone(self.initstring, timeout=1)
        cache['test'] = 'test'
        time.sleep(3)
        def tmp(): #@IgnorePep8
            cache['test']
        self.assertRaises(KeyError, tmp)


class CacheCull(Cache):

    def test_cull(self):
        cache = self._makeone(self.initstring, max_entries=1)
        cache['test'] = 'test'
        cache['test2'] = 'test'
        cache['test2'] = 'test'
        self.assertEquals(len(cache), 1)


class TestSimpleCache(CacheCull, unittest.TestCase):

    initstring = 'simple://'

    @property
    def _makeone(self):
        from shove.cache import SimpleCache
        return SimpleCache


class TestSimpleLRUCache(NoTimeout, unittest.TestCase):

    initstring = 'simplelru://'

    @property
    def _makeone(self):
        from shove.cache import SimpleLRUCache
        return SimpleLRUCache


class TestMemoryCache(CacheCull, unittest.TestCase):

    initstring = 'memory://'

    @property
    def _makeone(self):
        from shove.cache import MemoryCache
        return MemoryCache


class TestMemoryLRUCache(NoTimeout, unittest.TestCase):

    initstring = 'memlru://'

    @property
    def _makeone(self):
        from shove.cache import MemoryLRUCache
        return MemoryLRUCache


class TestFileCache(CacheCull, unittest.TestCase):

    initstring = 'file://test'

    @property
    def _makeone(self):
        from shove.cache import FileCache
        return FileCache

    def tearDown(self):
        import shutil
        self.cache = None
        shutil.rmtree('test')


class TestFileLRUCache(NoTimeout, unittest.TestCase):

    initstring = 'filelru://test2'

    @property
    def _makeone(self):
        from shove.cache import FileLRUCache
        return FileLRUCache

    def tearDown(self):
        import shutil
        self.cache = None
        shutil.rmtree('test2')


class TestDBCache(CacheCull, unittest.TestCase):

    initstring = 'sqlite:///'

    @property
    def _makeone(self):
        from shove.caches.db import DBCache
        return DBCache


if not PY3:
    class TestMemcache(Cache, Spawn, unittest.TestCase):

        initstring = 'memcache://localhost:11211'
        cmd = ['memcached']

        @property
        def _makeone(self):
            from shove.caches.memcached import MemCache
            return MemCache

    class TestRedisCache(Cache, Spawn, unittest.TestCase):

        initstring = 'redis://localhost:6379/0'
        cmd = ['redis-server']

        @property
        def _makeone(self):
            from shove.caches.redisdb import RedisCache
            return RedisCache


if __name__ == '__main__':
    unittest.main()
