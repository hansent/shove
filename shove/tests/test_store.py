# -*- coding: utf-8 -*-

from stuf.six import PY3, unittest


class EventualStore(object):

    def setUp(self):
        from shove import Shove
        self.store = Shove(self.initstring, compress=True)

    def tearDown(self):
        self.store.close()

    def test__getitem__(self):
        self.store['max'] = 3
        self.assertEqual(self.store['max'], 3)

    def test__setitem__(self):
        self.store['max'] = 3
        self.assertEqual(self.store['max'], 3)

    def test__delitem__(self):
        self.store['max'] = 3
        del self.store['max']
        self.assertEqual('max' in self.store, False)

    def test_get(self):
        self.store['max'] = 3
        self.assertEqual(self.store.get('min'), None)

    def test__cmp__(self):
        from shove import Shove
        tstore = Shove()
        self.store['max'] = 3
        tstore['max'] = 3
        self.assertEqual(self.store, tstore)

    def test__len__(self):
        self.store['max'] = 3
        self.store['min'] = 6
        self.assertEqual(len(self.store), 2)

    def test_items(self):
        self.store['max'] = 3
        self.store['min'] = 6
        self.store['pow'] = 7
        slist = list(self.store.items())
        self.assertEqual(('min', 6) in slist, True)

    def test_keys(self):
        self.store['max'] = 3
        self.store['min'] = 6
        self.store['pow'] = 7
        slist = list(self.store.keys())
        self.assertEqual('min' in slist, True)

    def test_values(self):
        self.store['max'] = 3
        self.store['min'] = 6
        self.store['pow'] = 7
        slist = list(self.store.values())
        self.assertEqual(6 in slist, True)

    def test_pop(self):
        self.store['max'] = 3
        self.store['min'] = 6
        item = self.store.pop('min')
        self.assertEqual(item, 6)

    def test_setdefault(self):
        self.store['max'] = 3
        self.store['min'] = 6
        self.assertEqual(self.store.setdefault('pow', 8), 8)
        self.assertEqual(self.store['pow'], 8)

    def test_update(self):
        from shove import Shove
        tstore = Shove()
        tstore['max'] = 3
        tstore['min'] = 6
        tstore['pow'] = 7
        self.store['max'] = 2
        self.store['min'] = 3
        self.store['pow'] = 7
        self.store.update(tstore)
        self.assertEqual(self.store['min'], 6)


class Store(EventualStore):

    def test_clear(self):
        self.store['max'] = 3
        self.store['min'] = 6
        self.store['pow'] = 7
        self.store.clear()
        self.assertEqual(len(self.store), 0)

    def test_popitem(self):
        self.store['max'] = 3
        self.store['min'] = 6
        self.store['pow'] = 7
        item = self.store.popitem()
        self.assertEqual(len(item) + len(self.store), 4)


class SyncStore(Store):

    def test_close(self):
        self.store.close()
        self.assertEqual(self.store, None)

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
        self.store.sync()
        del self.store['max']
        self.assertEqual('max' in self.store, False)

    def test_get(self):
        self.store['max'] = 3
        self.store.sync()
        self.assertEqual(self.store.get('min'), None)

    def test__cmp__(self):
        from shove import Shove
        tstore = Shove()
        self.store['max'] = 3
        tstore['max'] = 3
        self.store.sync()
        tstore.sync()
        self.assertEqual(self.store, tstore)


class TestSimpleStore(Store, unittest.TestCase):

    initstring = 'simple://'


class TestMemoryStore(Store, unittest.TestCase):

    initstring = 'memory://'


class TestFileStore(Store, unittest.TestCase):

    initstring = 'file://test'

    def tearDown(self):
        import shutil
        self.store.close()
        shutil.rmtree('test')


class TestDBMStore(SyncStore, unittest.TestCase):

    initstring = 'dbm://test.dbm'

    def tearDown(self):
        import os
        self.store.close()
        os.remove('test.dbm')


class TestDBStore(Store, unittest.TestCase):

    initstring = 'sqlite://'


class TestMongoDBStore(SyncStore, unittest.TestCase):

    initstring = 'mongodb://127.0.0.1:27017/shove/shove'

    def tearDown(self):
        self.store.clear()

    def test_close(self):
        pass


@unittest.skip('reason')
class TestFTPStore(SyncStore, unittest.TestCase):

    initstring = 'put ftp string here'

    def setUp(self):
        from shove import Shove
        self.store = Shove(self.ftpstring, compress=True)

    def tearDown(self):
        self.store.clear()
        self.store.close()


@unittest.skip('reason')
class TestS3Store(SyncStore, unittest.TestCase):

    initstring = 's3 test string here'

    def tearDown(self):
        self.store.clear()
        self.store.close()


if not PY3:
    class TestZODBStore(Store, unittest.TestCase):

        initstring = 'zodb://test.db'

        def tearDown(self):
            self.store.close()
            import os
            os.remove('test.db')
            os.remove('test.db.index')
            os.remove('test.db.tmp')
            os.remove('test.db.lock')

    class TestDurusStore(Store, unittest.TestCase):

        initstring = 'durus://test.durus'

        def tearDown(self):
            import os
            self.store.close()
            os.remove('test.durus')

    class TestRedisStore(Store, unittest.TestCase):

        initstring = 'redis://localhost:6379/0'

        def tearDown(self):
            self.store.clear()
            self.store.close()

    class TestBSDBStore(Store, unittest.TestCase):

        initstring = 'bsddb://test.db'

        def tearDown(self):
            import os
            self.store.close()
            os.remove('test.db')

    class TestCassandraStore(EventualStore, unittest.TestCase):

        def setUp(self):
            from shove import Shove
            from pycassa.system_manager import SystemManager  # @UnresolvedImport @IgnorePep8
            system_manager = SystemManager('localhost:9160')
            try:
                system_manager.create_column_family('Foo', 'shove')
            except:
                pass
            self.store = Shove('cassandra://localhost:9160/Foo/shove')

        def tearDown(self):
            self.store.clear()
            self.store.close()
            from pycassa.system_manager import SystemManager  # @UnresolvedImport @IgnorePep8
            system_manager = SystemManager('localhost:9160')
            system_manager.drop_column_family('Foo', 'shove')

    @unittest.skip('reason')
    class TestHDF5Store(Store, unittest.TestCase):

        initstring = 'hdf5://test.hdf5/test'

        def setUp(self):
            from shove import Shove
            self.store = Shove()

        def tearDown(self):
            import os
            self.store.close()
            try:
                os.remove('test.hdf5')
            except OSError:
                pass

    @unittest.skip('reason')
    class TestLevelDBStore(unittest.TestCase):

        initstring = 'leveldb://test'

        def tearDown(self):
            import shutil
            shutil.rmtree('test')


if __name__ == '__main__':
    unittest.main()
