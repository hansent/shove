# -*- coding: utf-8 -*-
'''shove test mixins'''


class Spawn(object):

    shell = False

    @staticmethod
    def setUpModule():
        import os
        from tempfile import mkdtemp
        TMP = mkdtemp()
        os.environ['TEST_DIR'] = TMP
        os.chdir(TMP)

    @staticmethod
    def tearDownModule():
        import os
        from shutil import rmtree
        rmtree(os.environ['TEST_DIR'])
        del os.environ['TEST_DIR']

    @classmethod
    def setUpClass(cls):
        from subprocess32 import Popen  # @UnresolvedImport
        cls.process = Popen(
            cls.cmd, stdout=open('/dev/null', 'w'), shell=cls.shell
        )

    @classmethod
    def tearDownClass(cls):
        cls.process.kill()
