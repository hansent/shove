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
#    3. Neither the name of Django nor the names of its contributors may be used
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

'''Subversion store.'''

import os
import urllib
import pysvn
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove import BaseStore, synchronized

__all__ = ['SvnStore']


class SvnStore(BaseStore):

    '''Subversion store.'''    
    
    def __init__(self, engine=None, **kw):
        super(SvnStore, self).__init__(**kw)
        local, remote = kw.get('local'), kw.get('remote')
        user, password = kw.get('user'), kw.get('password') 
        if engine is not None:
            host, query = engine.split('?')
            local = host.split('/', 2)[2]
            if '@' in local:
                auth, local = local.split('@')
                user, password = auth.split(':')
            remote = query.split('=')[1]
        self._client = pysvn.Client()
        if user is not None: self._client.set_username(user)
        if password is not None: self._client.set_password(password)
        try:
            self._client.info2(remote)
        except pysvn.ClientError:
            self._client.mkdir(remote)          
        try:
            self._client.info(local)
        except pysvn.ClientError:              
            self._client.checkout(remote, local)
        self._local, self._remote = local, remote

    @synchronized
    def __getitem__(self, key):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        '''
        try:
            return pickle.loads(self._client.cat(self._key_to_file(key)))
        except:
            raise KeyError()

    @synchronized
    def __setitem__(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.        
        '''
        fname = self._key_to_file(key)
        pickle.dump(value, open(fname, 'wb'), 2)
        if key not in self: self._client.add(fname)
        self._client.checkin([fname], 'Adding %s' % fname)            
        
    @synchronized
    def __delitem__(self, key):
        '''Delete a key from the cache, failing silently.

        @param key Keyword of item in cache.
        '''
        fname = self._key_to_file(key)
        self._client.remove(fname)
        self._client.checkin([fname], 'Removing %s' % fname)

    @synchronized
    def keys(self):
        return list(str(i.name.split('/')[-1]) for i in self._client.ls(self._local))

    def _key_to_file(self, key):
        '''Gives the filesystem path for a key.'''
        return os.path.join(self._local, urllib.quote_plus(key))