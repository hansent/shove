import unittest
import time
from shove import Shove

class TestMemcached(unittest.TestCase):

    initstring = 'memcache://localhost'

    def setUp(self): 
        self.cache = Shove('simple://', self.initstring, compressed=True)

    def tearDown(self): 
        self.cache = None    
    
    def test_getitem(self):
        '''Tests __setitem__ and __setitem__ on MemCache.'''
        self.cache['test'] = 'test'
        self.assertEqual(self.cache['test'], 'test')

    def test_setitem(self):
        '''Tests set and get on MemCache.'''
        self.cache['test'] = 'test'
        self.assertEqual(self.cache['test'], 'test')

    def test_delitem(self):
        '''Tests __delitem__ on MemCache.'''
        self.cache['test'] = 'test'
        del self.cache['test']
        self.assertEqual(self.cache['test'], None)

    def test_in_true(self):
        '''Tests in (true) on MemCache.'''
        self.cache['test'] = 'test'
        self.assertEqual('test' in self.cache, True)

    def test_in_false(self):
        '''Tests in (false) on MemCache.'''
        self.cache['test2'] = 'test'
        self.assertEqual('test2' in self.cache, False)

    def test_get(self):
        self.assertEqual(self.cache.get('min'), None)        

    def test_timeout(self):
        '''Tests timeout in MemCached.'''
        cache = Shove('simple://', self.initstring, timeout=1)
        cache['test'] = 'test'
        time.sleep(1)
        self.assertEqual(cache['test'], None)
        

if __name__ == '__main__':
    unittest.main()        