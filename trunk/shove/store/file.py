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

'''Filesystem-based object store

shove's psuedo-URL for filesystem-based stores follows the form:

file://<path>

Where the path is a URL path to a directory on a local filesystem.
Alternatively, a native pathname to the directory can be passed as the 'engine'
argument.
'''

import os
import urllib
from shove import BaseStore

__all__ = ['FileStore']


class FileStore(BaseStore):

    '''File-based store.'''    
    
    def __init__(self, engine, **kw):
        super(FileStore, self).__init__(**kw)
        if engine.startswith('file://'):
            engine = urllib.url2pathname(engine.split('://')[1])
        self._dir = engine
        # Create directory
        if not os.path.exists(self._dir): self._createdir()        

    def __getitem__(self, key):
        try:
            return self.loads(open(self._key_to_file(key), 'rb').read())
        except:
            raise KeyError('Key not found.')

    def __setitem__(self, key, value):
        try:
            open(self._key_to_file(key), 'wb').write(self.dumps(value))
        except (IOError, OSError): pass

    def __delitem__(self, key):
        try:
            os.remove(self._key_to_file(key))
        except (IOError, OSError): pass

    def __contains__(self, key):
        return os.path.exists(self._key_to_file(key))       

    def keys(self):
        '''Returns a list of keys in the store.'''
        try:
            return os.listdir(self._dir)
        except (IOError, OSError): return list()            

    def _createdir(self):
        '''Creates the store directory.'''
        try:
            os.makedirs(self._dir)
        except OSError:
            raise EnvironmentError('Cache directory "%s" does not exist and ' \
                'could not be created' % self._dir)

    def _key_to_file(self, key):
        '''Gives the filesystem path for a key.'''
        return os.path.join(self._dir, urllib.quote_plus(key))