import unittest
import time
from shove.cache.memcached import MemCached

class TestMemcached(unittest.TestCase):

    initstring = 'memcache://localhost'

    def setUp(self): 
        self.cache = MemCached(self.initstring, timeout=1)

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
        self.assertEqual('test' in self.cache, False)

    def test_get(self):
        self.assertEqual(self.cache.get('min'), None)        

    def test_timeout(self):
        '''Tests timeout in MemCached.'''        
        cache = MemCached(self.initstring, timeout=1)
        cache['test'] = 'test'
        time.sleep(1)
        def tmp(): cache['test']            
        self.assertRaises(KeyError, tmp)
        

if __name__ == '__main__':
    unittest.main()        