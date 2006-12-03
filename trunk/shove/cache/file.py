# Copyright (c) 2005, the Lawrence Journal-World
# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
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
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''File-based cache

shove's psuedo-URL for file caches follows the form:

file://<path>

Where the path is a URL path to a directory on a local filesystem.
Alternatively, a native pathname to the directory can be passed as the 'engine'
argument.
'''

import os
import time
import urllib
import random
from shove.cache.simple import SimpleCache

__all__ = ['FileCache']


class FileCache(SimpleCache):

    '''File-based cache backend'''    
    
    def __init__(self, engine, **kw):
        super(FileCache, self).__init__(engine, **kw)
        if engine.startswith('file://'): engine = engine.split('://')[1]
        # Create directory
        self._dir = engine
        if not os.path.exists(self._dir): self._createdir()
        # Remove unneeded methods and attributes
        del self._cache, self._expire_info

    def __getitem__(self, key):
        try:
            try:
                fname = self._key_to_file(key)
                local = open(fname, 'rb')
                exp = self.loads(local.readline() + local.readline())
                # Remove item if time has expired.
                if exp < time.time():
                    local.close()
                    os.remove(fname)
                value = self.loads(local.readline() + local.readline())
                return value
            finally:
                local.close()
        except:
            raise KeyError('Key not in cache.')
                

    def __setitem__(self, key, value):
        try:
            try:
                fname = self._key_to_file(key)
                if len(self) > self._max_entries: self._cull()
                local = open(fname, 'wb')
                local.write(self.dumps(time.time() + self.timeout))
                local.write(self.dumps(value))
            finally:
                local.close()
        except:
            raise KeyError('%s' % key)            

    def __delitem__(self, key):
        try:
            os.remove(self._key_to_file(key))
        except (IOError, OSError):
            raise KeyError('%s' % key)

    def __contains__(self, key):
        return os.path.exists(self._key_to_file(key))
    
    def __len__(self):
        return len(os.listdir(self._dir))

    def _cull(self):
        '''Remove items in cache to make room.'''
        filelist, num = os.listdir(self._dir), 0
        for fname in filelist:
            if num < self._maxcull:
                # Remove expired items from cache.
                try:
                    self[fname]
                except KeyError:
                    num += 1
            else: break
        if len(self._cache) >= self._max_entries:
            for i in range(self._maxcull): del self[random.choice(filelist)]

    def _createdir(self):
        '''Creates the cache directory.'''
        try:
            os.makedirs(self._dir)
        except OSError:
            raise EnvironmentError('Cache directory "%s" does not exist and ' \
                'could not be created' % self._dir)

    def _key_to_file(self, key):
        '''Gives the filesystem path for a key.'''
        return os.path.join(self._dir, urllib.quote_plus(key))