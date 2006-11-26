# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of psilib nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Unit tests for wsgistate.'''

import unittest
import StringIO
import copy
import os
import time
from wsgistate import *
import urlparse


class TestWsgiState(unittest.TestCase):
    
    '''Test cases for wsgistate.'''
        
    def dummy_sr(self, status, headers, exc_info=None):
        return headers
    
    def my_app(self, environ, start_response):
        session = environ['com.saddi.service.session'].session
        count = session.get('count', 0) + 1
        session['count'] = count
        environ['count'] = count
        headers = start_response('200 OK', [])
        if headers: environ['cookie'] = headers[0][1]
        return environ

    def my_app2(self, environ, start_response):
        session = environ['com.saddi.service.session'].session
        count = session.get('count', 0) + 1
        session['count'] = count
        environ['count'] = count
        headers = start_response('200 OK', [])
        return environ

    def my_app3(self, environ, start_response):
        start_response('200 OK', [])
        return ['passed']

    def test_sc_set_getitem(self):
        '''Tests __setitem__ and __setitem__ on SimpleCache.'''
        cache = simple.SimpleCache()
        cache['test'] = 'test'
        self.assertEqual(cache['test'], 'test')

    def test_sc_set_get(self):
        '''Tests set and get on SimpleCache.'''
        cache = simple.SimpleCache()
        cache.set('test', 'test')
        self.assertEqual(cache.get('test'), 'test')

    def test_sc_delitem(self):
        '''Tests __delitem__ on SimpleCache.'''
        cache = simple.SimpleCache()
        cache['test'] = 'test'
        del cache['test']
        self.assertEqual(cache.get('test'), None)

    def test_sc_set_get(self):
        '''Tests delete on SimpleCache.'''
        cache = simple.SimpleCache()
        cache.set('test', 'test')
        cache.delete('test')
        self.assertEqual(cache.get('test'), None)

    def test_set_getmany(self):
        '''Tests delete on SimpleCache.'''
        cache = simple.SimpleCache()
        cache.set('test', 'test')
        cache.set('test2', 'test2')
        self.assertEqual(sorted(cache.get_many(('test', 'test2')).values()), ['test', 'test2'])

    def test_sc_in_true(self):
        '''Tests in (true) on SimpleCache.'''
        cache = simple.SimpleCache()
        cache.set('test', 'test')
        self.assertEqual('test' in cache, True)

    def test_sc_in_false(self):
        '''Tests in (false) on SimpleCache.'''
        cache = simple.SimpleCache()
        cache.set('test2', 'test')
        self.assertEqual('test' in cache, False)

    def test_sc_timeout(self):
        '''Tests timeout in SimpleCache.'''
        cache = simple.SimpleCache(timeout=1)
        cache.set('test', 'test')
        time.sleep(1)
        self.assertEqual(cache.get('test'), None)        

    def test_mc_set_getitem(self):
        '''Tests __setitem__ and __setitem__ on MemoryCache.'''
        cache = memory.MemoryCache()
        cache['test'] = 'test'
        self.assertEqual(cache['test'], 'test')

    def test_mc_set_get(self):
        '''Tests set and get on MemoryCache.'''
        cache = memory.MemoryCache()
        cache.set('test', 'test')
        self.assertEqual(cache.get('test'), 'test')

    def test_mc_delitem(self):
        '''Tests __delitem__ on MemoryCache.'''
        cache = memory.MemoryCache()
        cache['test'] = 'test'
        del cache['test']
        self.assertEqual(cache.get('test'), None)

    def test_mc_set_get(self):
        '''Tests delete on MemoryCache.'''
        cache = memory.MemoryCache()
        cache.set('test', 'test')
        cache.delete('test')
        self.assertEqual(cache.get('test'), None)

    def test_mc_set_getmany(self):
        '''Tests delete on MemoryCache.'''
        cache = memory.MemoryCache()
        cache.set('test', 'test')
        cache.set('test2', 'test2')
        self.assertEqual(sorted(cache.get_many(('test', 'test2')).values()), ['test', 'test2'])

    def test_mc_in_true(self):
        '''Tests in (true) on MemoryCache.'''
        cache = memory.MemoryCache()
        cache.set('test', 'test')
        self.assertEqual('test' in cache, True)

    def test_mc_in_false(self):
        '''Tests in (false) on MemoryCache.'''
        cache = memory.MemoryCache()
        cache.set('test2', 'test')
        self.assertEqual('test' in cache, False)

    def test_mc_timeout(self):
        '''Tests timeout in MemoryCache.'''
        cache = memory.MemoryCache(timeout=1)
        cache.set('test', 'test')
        time.sleep(1)
        self.assertEqual(cache.get('test'), None)           

    def test_fc_set_getitem(self):
        '''Tests __setitem__ and __setitem__ on FileCache.'''
        cache = file.FileCache('test_wsgistate')
        cache['test'] = 'test'
        self.assertEqual(cache['test'], 'test')

    def test_fc_set_get(self):
        '''Tests set and get on FileCache.'''
        cache = file.FileCache('test_wsgistate')
        cache.set('test', 'test')
        self.assertEqual(cache.get('test'), 'test')

    def test_fc_delitem(self):
        '''Tests __delitem__ on FileCache.'''
        cache = file.FileCache('test_wsgistate')
        cache['test'] = 'test'
        del cache['test']
        self.assertEqual(cache.get('test'), None)

    def test_fc_set_get(self):
        '''Tests delete on FileCache.'''
        cache = file.FileCache('test_wsgistate')
        cache.set('test', 'test')
        cache.delete('test')
        self.assertEqual(cache.get('test'), None)

    def test_fc_set_getmany(self):
        '''Tests delete on FileCache.'''
        cache = file.FileCache('test_wsgistate')
        cache.set('test', 'test')
        cache.set('test2', 'test2')
        self.assertEqual(sorted(cache.get_many(('test', 'test2')).values()), ['test', 'test2'])

    def test_fc_in_true(self):
        '''Tests in (true) on FileCache.'''
        cache = file.FileCache('test_wsgistate')
        cache.set('test', 'test')
        self.assertEqual('test' in cache, True)

    def test_fc_in_false(self):
        '''Tests in (false) on FileCache.'''
        cache = file.FileCache('test_wsgistate')
        cache.set('test2', 'test')
        self.assertEqual('test' in cache, False)

    def test_fc_timeout(self):
        '''Tests timeout in FileCache.'''
        cache = file.FileCache('test_wsgistate', timeout=1)
        cache.set('test', 'test')
        time.sleep(1)
        self.assertEqual(cache.get('test'), None)           
    
    def test_db_set_getitem(self):
        '''Tests __setitem__ and __setitem__ on DbCache.'''
        cache = db.DbCache('sqlite:///:memory:')
        cache['test'] = 'test'
        self.assertEqual(cache['test'], 'test')

    def test_db_set_get(self):
        '''Tests set and get on DbCache.'''
        cache = db.DbCache('sqlite:///:memory:')
        cache.set('test', 'test')
        self.assertEqual(cache.get('test'), 'test')

    def test_db_delitem(self):
        '''Tests __delitem__ on DbCache.'''
        cache = db.DbCache('sqlite:///:memory:')
        cache['test'] = 'test'
        del cache['test']
        self.assertEqual(cache.get('test'), None)

    def test_db_set_get(self):
        '''Tests delete on DbCache.'''
        cache = db.DbCache('sqlite:///:memory:')
        cache.set('test', 'test')
        cache.delete('test')
        self.assertEqual(cache.get('test'), None)

    def test_db_set_getmany(self):
        '''Tests delete on DbCache.'''
        cache = db.DbCache('sqlite:///:memory:')
        cache.set('test', 'test')
        cache.set('test2', 'test2')
        self.assertEqual(sorted(cache.get_many(('test', 'test2')).values()), ['test', 'test2'])

    def test_db_in_true(self):
        '''Tests in (true) on DbCache.'''
        cache = db.DbCache('sqlite:///:memory:')
        cache.set('test', 'test')
        self.assertEqual('test' in cache, True)

    def test_db_in_false(self):
        '''Tests in (false) on DbCache.'''
        cache = db.DbCache('sqlite:///:memory:')
        cache.set('test2', 'test')
        self.assertEqual('test' in cache, False)

    def test_db_timeout(self):
        '''Tests timeout in DbCache.'''
        cache = db.DbCache('sqlite:///:memory:', timeout=1)
        cache.set('test', 'test')
        time.sleep(2)
        self.assertEqual(cache.get('test'), None)         

    def test_mcd_set_getitem(self):
        '''Tests __setitem__ and __setitem__ on MemCache.'''
        cache = memcached.MemCached('localhost')
        cache['test'] = 'test'
        self.assertEqual(cache['test'], 'test')

    def test_mcd_set_get(self):
        '''Tests set and get on MemCache.'''
        cache = memcached.MemCached('localhost')
        cache.set('test', 'test')
        self.assertEqual(cache.get('test'), 'test')

    def test_mcd_delitem(self):
        '''Tests __delitem__ on MemCache.'''
        cache = memcached.MemCached('localhost')
        cache['test'] = 'test'
        del cache['test']
        self.assertEqual(cache.get('test'), None)

    def test_mcd_set_get(self):
        '''Tests delete on MemCache.'''
        cache = memcached.MemCached('localhost')
        cache.set('test', 'test')
        cache.delete('test')
        self.assertEqual(cache.get('test'), None)

    def test_mcd_set_getmany(self):
        '''Tests delete on MemCache.'''
        cache = memcached.MemCached('localhost')
        cache.set('test', 'test')
        cache.set('test2', 'test2')
        self.assertEqual(sorted(cache.get_many(('test', 'test2')).values()), ['test', 'test2'])

    def test_mcd_in_true(self):
        '''Tests in (true) on MemCache.'''
        cache = memcached.MemCached('localhost')
        cache.set('test', 'test')
        self.assertEqual('test' in cache, True)

    def test_mcd_in_false(self):
        '''Tests in (false) on MemCache.'''
        cache = memcached.MemCached('localhost')
        cache.set('test2', 'test')
        self.assertEqual('test' in cache, False)

    def test_mcb_timeout(self):
        '''Tests timeout in DbCache.'''
        cache = memcached.MemCached('localhost', timeout=1)
        cache.set('test', 'test')
        time.sleep(1)
        self.assertEqual(cache.get('test'), None)          

    def test_cookiesession_sc(self):
        '''Tests session cookies with SimpleCache.'''
        testc = simple.SimpleCache()
        cache = session.SessionCache(testc)
        csession = session.CookieSession(self.my_app, cache)
        cookie = csession({}, self.dummy_sr)['cookie']
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_cookiesession_mc(self):
        '''Tests session cookies with MemoryCache.'''
        testc = memory.MemoryCache()
        cache = session.SessionCache(testc)
        csession = session.CookieSession(self.my_app, cache)
        cookie = csession({}, self.dummy_sr)['cookie']
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)
        
    def test_cookiesession_fc(self):
        '''Tests session cookies with FileCache.'''
        testc = file.FileCache('test_wsgistate')
        cache = session.SessionCache(testc)
        csession = session.CookieSession(self.my_app, cache)
        cookie = csession({}, self.dummy_sr)['cookie']
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_cookiesession_dc(self):
        '''Tests session cookies with DbCache.'''
        testc = db.DbCache('sqlite:///:memory:')
        cache = session.SessionCache(testc)
        csession = session.CookieSession(self.my_app, cache)
        cookie = csession({}, self.dummy_sr)['cookie']
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_cookiesession_mdc(self):
        '''Tests session cookies with MemCached.'''
        testc = memcached.MemCached('localhost')
        cache = session.SessionCache(testc)
        csession = session.CookieSession(self.my_app, cache)
        cookie = csession({}, self.dummy_sr)['cookie']
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_cookiesession_sc(self):
        '''Tests session cookies with SimpleCache decorator.'''
        @simple.session()
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        cookie = tapp({}, self.dummy_sr)['cookie']
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_cookiesession_mc(self):
        '''Tests session cookies with MemoryCache decorator.'''
        @memory.session()
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        cookie = tapp({}, self.dummy_sr)['cookie']
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_cookiesession_fc(self):
        '''Tests session cookies with FileCache decorator.'''
        @file.session('test_wsgistate')
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        cookie = tapp({}, self.dummy_sr)['cookie']
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_cookiesession_db(self):
        '''Tests session cookies with DbCache decorator.'''
        @db.session('sqlite:///:memory:')
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        cookie = tapp({}, self.dummy_sr)['cookie']
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_cookiesession_mc(self):
        '''Tests session cookies with memcached decorator.'''
        @memcached.session('localhost')
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        cookie = tapp({}, self.dummy_sr)['cookie']
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':cookie}, self.dummy_sr)
        self.assertEqual(result['count'], 4)          

    def test_random_cookiesession_sc(self):
        '''Tests random session cookies with SimpleCache.'''
        testc = simple.SimpleCache()
        cache = session.SessionCache(testc, random=True)
        csession = session.CookieSession(self.my_app, cache)
        result = csession({}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_random_cookiesession_mc(self):
        '''Tests random session cookies with MemoryCache.'''
        testc = memory.MemoryCache()
        cache = session.SessionCache(testc, random=True)
        csession = session.CookieSession(self.my_app, cache)
        result = csession({}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)
        
    def test_random_cookiesession_fc(self):
        '''Tests random session cookies with FileCache.'''
        testc = file.FileCache('test_wsgistate')
        cache = session.SessionCache(testc, random=True)
        csession = session.CookieSession(self.my_app, cache)
        result = csession({}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_random_cookiesession_dc(self):
        '''Tests random session cookies with DbCache.'''
        testc = db.DbCache('sqlite:///:memory:')
        cache = session.SessionCache(testc, random=True)
        csession = session.CookieSession(self.my_app, cache)
        result = csession({}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_random_cookiesession_mdc(self):
        '''Tests random session cookies with MemCached.'''
        testc = memcached.MemCached('localhost')
        cache = session.SessionCache(testc, random=True)
        csession = session.CookieSession(self.my_app, cache)
        result = csession({}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = csession({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_random_cookiesession_sc(self):
        '''Tests random session cookies with SimpleCache decorator.'''
        @simple.session(random=True)
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        result = tapp({}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_random_cookiesession_mc(self):
        '''Tests random session cookies with MemoryCache decorator.'''
        @memory.session(random=True)
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        result = tapp({}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_random_cookiesession_fc(self):
        '''Tests random session cookies with FileCache decorator.'''
        @file.session('test_wsgistate', random=True)
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        result = tapp({}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_random_cookiesession_db(self):
        '''Tests random session cookies with DbCache decorator.'''
        @db.session('sqlite:///:memory:', random=True)
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        result = tapp({}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_random_cookiesession_mcd(self):
        '''Tests random session cookies with memcached decorator.'''
        @memcached.session('localhost', random=True)
        def tapp(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        result = tapp({}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        result = tapp({'HTTP_COOKIE':result['cookie']}, self.dummy_sr)
        self.assertEqual(result['count'], 4)                

    def test_urlsession_sc(self):
        '''Tests URL encoded sessions with SimpleCache.'''
        testc = simple.SimpleCache()
        cache = session.SessionCache(testc)
        csession = session.URLSession(self.my_app2, cache)
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_urlsession_mc(self):
        '''Tests URL encoded sessions with MemoryCache.'''
        testc = memory.MemoryCache()
        cache = session.SessionCache(testc)
        csession = session.URLSession(self.my_app2, cache)
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)
        
    def test_urlsession_fc(self):
        '''Tests URL encoded sessions with FileCache.'''
        testc = file.FileCache('test_wsgistate')
        cache = session.SessionCache(testc)
        csession = session.URLSession(self.my_app2, cache)
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_urlsession_dc(self):
        '''Tests URL encoded sessions with DbCache.'''
        testc = db.DbCache('sqlite:///:memory:')
        cache = session.SessionCache(testc)
        csession = session.URLSession(self.my_app2, cache)
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_urlsession_mdc(self):
        '''Tests URL encoded sessions with MemCached.'''
        testc = memcached.MemCached('localhost')
        cache = session.SessionCache(testc)
        csession = session.URLSession(self.my_app2, cache)
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_urlsession_sc(self):
        '''Tests URL encoded sessions with SimpleCache.'''
        @simple.urlsession()
        def csession(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_urlsession_mc(self):
        '''Tests URL encoded sessions with MemoryCache decorator.'''
        @memory.urlsession()
        def csession(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)
        
    def test_dec_urlsession_fc(self):
        '''Tests URL encoded sessions with FileCache decorator.'''
        @file.urlsession('test_wsgistate')
        def csession(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_urlsession_dc(self):
        '''Tests URL encoded sessions with DbCache decorator.'''
        @db.urlsession('sqlite:///:memory:')
        def csession(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)

    def test_dec_urlsession_mdc(self):
        '''Tests URL encoded sessions with MemCached decorator.'''
        @memcached.urlsession('localhost')
        def csession(environ, start_response):
            session = environ['com.saddi.service.session'].session
            count = session.get('count', 0) + 1
            session['count'] = count
            environ['count'] = count
            headers = start_response('200 OK', [])
            if headers: environ['cookie'] = headers[0][1]
            return environ
        url = csession({}, self.dummy_sr)[0].split()[-1]
        query = urlparse.urlsplit(url)[3]
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        csession({'QUERY_STRING':query}, self.dummy_sr)
        result = csession({'QUERY_STRING':query}, self.dummy_sr)
        self.assertEqual(result['count'], 4)        

    def test_wsgimemoize_default_sc(self):
        '''Tests default memoizing with SimpleCache decorator.'''
        testc = simple.SimpleCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_default_mc(self):
        '''Tests default memoizing with MemoryCache.'''
        testc = memory.MemoryCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_default_fc(self):
        '''Tests default memoizing with FileCache.'''
        testc = file.FileCache('test_wsgistate')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_default_db(self):
        '''Tests default memoizing with DbCache.'''
        testc = db.DbCache('sqlite:///:memory:')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_default_mcd(self):
        '''Tests default memoizing with MemCached.'''
        testc = memcached.MemCached('localhost')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_dec_wsgimemoize_default_sc(self):
        '''Tests default memoizing with SimpleCache decorator.'''
        @simple.memoize()
        def cacheapp(environ, start_response):
            start_response('200 OK', [])
            return ['passed']
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_dec_wsgimemoize_default_mc(self):
        '''Tests default memoizing with MemoryCache.'''
        @memory.memoize()
        def cacheapp(environ, start_response):
            start_response('200 OK', [])
            return ['passed']
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_dec_wsgimemoize_default_fc(self):
        '''Tests default memoizing with FileCache.'''
        @file.memoize('test_wsgistate')
        def cacheapp(environ, start_response):
            start_response('200 OK', [])
            return ['passed']
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_dec_wsgimemoize_default_db(self):
        '''Tests default memoizing with DbCache.'''
        @db.memoize('sqlite:///:memory:')
        def cacheapp(environ, start_response):
            start_response('200 OK', [])
            return ['passed']
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_dec_wsgimemoize_fault_mcd(self):
        '''Tests default memoizing with MemCached.'''
        @memcached.memoize('localhost')
        def cacheapp(environ, start_response):
            start_response('200 OK', [])
            return ['passed']
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)        

    def test_wsgimemoize_method_sc(self):
        '''Tests memoizing with HTTP method as part of the key with SimpleCache.'''
        testc = simple.SimpleCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_methods=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_method_mc(self):
        '''Tests memoizing with HTTP method as part of the key with MemoryCache.'''
        testc = memory.MemoryCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_methods=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_method_fc(self):
        '''Tests memoizing with HTTP method as part of the key with FileCache.'''
        testc = file.FileCache('test_wsgistate')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_methods=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_method_db(self):
        '''Tests memoizing with HTTP method as part of the key with DbCache.'''
        testc = db.DbCache('sqlite:///:memory:')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_methods=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_method_mcd(self):
        '''Tests memoizing with HTTP method as part of the key with MemCached.'''
        testc = memcached.MemCached('localhost')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_methods=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_user_info_sc(self):
        '''Tests memoizing with user info as part of the key with SimpleCache.'''
        testc = simple.SimpleCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET',
        'wsgi.input':StringIO.StringIO('num=12121&str1=test&state=NV&Submit=Submit')}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_user_info=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_user_info_mc(self):
        '''Tests memoizing with user info as part of the key with MemoryCache.'''
        testc = memory.MemoryCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET',
        'wsgi.input':StringIO.StringIO('num=12121&str1=test&state=NV&Submit=Submit')}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_user_info=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_user_info_fc(self):
        '''Tests memoizing with user info as part of the key with FileCache.'''
        testc = file.FileCache('test_wsgistate')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET',
        'wsgi.input':StringIO.StringIO('num=12121&str1=test&state=NV&Submit=Submit')}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_user_info=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_user_info_db(self):
        '''Tests memoizing with user info as part of the key with DbCache.'''
        testc = db.DbCache('sqlite:///:memory:')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET',
        'wsgi.input':StringIO.StringIO('num=12121&str1=test&state=NV&Submit=Submit')}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_user_info=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_user_info_mcd(self):
        '''Tests memoizing with user info as part of the key with MemCached.'''
        testc = memcached.MemCached('localhost')
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'GET',
        'wsgi.input':StringIO.StringIO('num=12121&str1=test&state=NV&Submit=Submit')}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, key_user_info=True)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_allowed_methods(self):
        '''Tests memoizing with HTTP method as part of the key with MemCached.'''
        testc = simple.SimpleCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'POST',
        'wsgi.input':StringIO.StringIO('num=12121&str1=test&state=NV&Submit=Submit')}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc, allowed_methods=set(['POST']))
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_wsgimemoize_not_allowed_methods(self):
        '''Tests memoizing with an unallowed HTTP method.'''
        testc = simple.SimpleCache()
        env = {'PATH_INFO':'/', 'REQUEST_METHOD':'POST',
        'wsgi.input':StringIO.StringIO('num=12121&str1=test&state=NV&Submit=Submit')}
        cacheapp = cache.WsgiMemoize(self.my_app3, testc)
        result1 = cacheapp(env, self.dummy_sr)
        result2 = cacheapp(env, self.dummy_sr)
        self.assertEqual(result1 == result2, True)

    def test_public(self):
        '''Tests correct setting of Cache-Control header "public".'''        
        @cache.public
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'public')
                                
    def test_private(self):
        '''Tests correct setting of Cache-Control header "private".'''
        @cache.private
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'private')
    
    def test_nocache(self):
        '''Tests correct setting of Cache-Control header "no-cache".'''
        @cache.nocache
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'no-cache')

    def test_nostore(self):
        '''Tests correct setting of Cache-Control header "no-store".'''
        @cache.nostore
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'no-store')

    def test_notransform(self):
        '''Tests correct setting of Cache-Control header "no-transform".'''
        @cache.notransform
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'no-transform')

    def test_revalidate(self):
        '''Tests correct setting of Cache-Control header "must-revalidate".'''
        @cache.revalidate
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'must-revalidate')              

    def test_proxyrevalidate(self):
        '''Tests correct setting of Cache-Control header "proxy-revalidate".'''
        @cache.proxyrevalidate
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'proxy-revalidate')

    def test_maxage(self):
        '''Tests correct setting of Cache-Control header "max-age".'''
        @cache.maxage(30)
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 'max-age=30')

    def test_smaxage(self):
        '''Tests correct setting of Cache-Control header "s-maxage".'''
        @cache.smaxage(30)
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 's-maxage=30')

    def test_vary(self):
        '''Tests correct setting of Vary header.'''
        @cache.vary(['Content-type'])
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Vary'], 'Content-type')

    def test_modified(self):
        '''Tests setting of Modified header.'''
        @cache.modified(30)
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual('Modified' in result, True)        

    def test_cachecontrol_combo(self):
        '''Tests correct setting of two Cache Control header settings.'''
        @cache.smaxage(30)
        @cache.private
        def app(environ, start_response):
            headers = start_response('200 OK', [])
            if headers: environ['headers'] = headers 
            return environ    
        result = dict(app({'REQUEST_METHOD':'GET'}, self.dummy_sr)['headers'])
        self.assertEqual(result['Cache-Control'], 's-maxage=30, private')         

    'modified'        

if __name__ == '__main__':
    unittest.main()
    try:
        os.rmdir('test_wsgistate')
    except IOError: pass