import unittest
import time
import os
from shove.cache.bsdb import BsdCache


class TestBsdCache(unittest.TestCase):

    initstring = 'bsddb://test.db'
    cacheclass = BsdCache

    def setUp(self): 
        self.cache = self.cacheclass(self.initstring)

    def tearDown(self): 
        self.cache._store.close()
        os.remove('test.db')
    
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
        cache = self.cacheclass(self.initstring, timeout=1)
        cache['test'] = 'test'
        time.sleep(1)
        def tmp(): cache['test']            
        self.assertRaises(KeyError, tmp)

    def test_cull(self):      
        cache = self.cacheclass(self.initstring, max_entries=1)
        cache['test'] = 'test'
        cache['test2'] = 'test'
        num = len(cache)
        self.assertEquals(num, 1)
        

if __name__ == '__main__':
    unittest.main()        