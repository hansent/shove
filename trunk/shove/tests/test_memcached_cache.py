import unittest
import time

class TestMemcached(unittest.TestCase):

    def setUp(self): 
        self.cache = Shove('simple://', 'memcached://localhost', compressed=True)

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
        self.assertEqual('test' in self.cache, False)

    def test_get(self):
        self.assertEqual(self.store.get('min'), None)        

    def test_timeout(self):
        '''Tests timeout in MemCached.'''
        cache = Shove('simple://', 'memcached://localhost', timeout=1)
        self.cache['test'] = 'test'
        time.sleep(1)
        self.assertEqual(self.cache['test'], None)
        

if __name__ == '__main__':
    unittest.main()        