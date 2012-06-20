# -*- coding: utf-8 -*-

from stuf.six import PY3, unittest


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
    from testresources import ResourcedTestCase, TestResourceManager

    class MemcachedManager(TestResourceManager):
        setUpCost = 10
        tearDownCost = 5

        def make(self, dependency_resources):
            from fabric.api import local
            local('memcached -d')

        def clean(self, resource):
            from fabric.api import local
            local('killall memcached')

    class TestMemcache(Cache, ResourcedTestCase):

        initstring = 'memcache://localhost:11211'
        resources = (('server', MemcachedManager()),)

        @property
        def _makeone(self):
            from shove.caches.memcached import MemCache
            return MemCache

    class RedisManager(TestResourceManager):
        setUpCost = 10
        tearDownCost = 5

        def make(self, dependency_resources):
            import os
            from tempfile import mkdtemp
            from fabric.api import local
            self.tmp = mkdtemp()
            os.chdir(self.tmp)
            local('redis-server --daemonize=yes')

        def clean(self, resource):
            import os
            import shutil
            from fabric.api import local
            local('killall redis-server')
            os.chdir(self.tmp)
            shutil.rmtree(self.tmp)

    class TestRedisCache(Cache, ResourcedTestCase):

        initstring = 'redis://localhost:6379/0'
        resources = (('server', RedisManager()),)

        @property
        def _makeone(self):
            from shove.caches.redisdb import RedisCache
            return RedisCache


def load_tests(loader, tests, pattern):
    from testresources import OptimisingTestSuite
    suite = unittest.TestSuite()
    suite.addTest(tests)
    suite.addTest(OptimisingTestSuite(tests))
    return suite

if __name__ == '__main__':
    unittest.main()
