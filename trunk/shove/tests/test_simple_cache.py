import unittest
from shove import Shove

class TestSimpleStore(unittest.TestCase):

    def setUp(self): 
        self.store = Shove('simple://', 'simple://', compressed=True)

    def tearDown(self): 
        self.store.close()

    def test__getitem__(self):
        self.store['max'] = 3
        self.store.sync()
        self.assertEqual(self.store['max'], 3)

    def test__setitem__(self):
        self.store['max'] = 3
        self.store.sync()
        self.assertEqual(self.store['max'], 3)

    def test__delitem__(self):
        self.store['max'] = 3
        del self.store['max']
        self.assertEqual('max' in self.store, False)

    def test_get(self):
        self.store['max'] = 3
        self.store.sync()
        self.assertEqual(self.store.get('min'), None)
        
if __name__ == '__main__':
    unittest.main()
