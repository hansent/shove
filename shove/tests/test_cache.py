# -*- coding: utf-8 -*-

from stuf.six import PY3, unittest


class Cache(object):

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

    def test_get(self):
        self.assertEqual(self.cache.get('min'), None)

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
        from shove.cache.core import SimpleCache
        return SimpleCache


class TestMemoryCache(CacheCull, unittest.TestCase):

    initstring = 'memory://'

    @property
    def _makeone(self):
        from shove.cache.core import MemoryCache
        return MemoryCache


class TestFileCache(CacheCull, unittest.TestCase):

    initstring = 'file://test'

    @property
    def _makeone(self):
        from shove.cache.core import FileCache
        return FileCache

    def tearDown(self):
        import os
        self.cache = None
        for x in os.listdir('test'):
            os.remove(os.path.join('test', x))
        os.rmdir('test')


class TestDbCache(CacheCull, unittest.TestCase):

    initstring = 'sqlite:///'

    @property
    def _makeone(self):
        from shove.cache.db import DBCache
        return DBCache


if not PY3:
    class TestMemcached(Cache, unittest.TestCase):

        initstring = 'memcache://localhost:11211'

        @property
        def _makeone(self):
            from shove.cache.memcached import MemCached
            return MemCached

    class TestRedisCache(Cache, unittest.TestCase):

        initstring = 'redis://localhost:6379/0'

        @property
        def _makeone(self):
            from shove.cache.redisdb import RedisCache
            return RedisCache


if __name__ == '__main__':
    unittest.main()
