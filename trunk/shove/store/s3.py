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
#    3. Neither the name of the Portable Site Information project nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
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

'''S3-accessed stores

shove's psuedo-URL for stores found on Amazon.com's S3 web service follows this
form:

s3://<s3_key>:<s3_secret>@<bucket>

<s3_key> is the Access Key issued by Amazon
<s3_secret> is the Secret Access Key issued by Amazon
<bucket> is the name of the storage bucket accessed through the S3 service
'''

try:
    from boto.connection import S3Connection
    from boto.key import Key
except ImportError:
    raise ImportError('Requires boto library.')
from shove import BaseStore


class S3Store(BaseStore):    

    def __init__(self, engine=None, **kw):
        super(S3Store, self).__init__(**kw)
        self._updated, self._keys = True, None
        key, secret, bucket = kw.get('key'), kw.get('secret'), kw.get('bucket')
        if engine is not None:
            auth, bucket = engine.split('://')[1].split('@')
            key, secret = auth.split(':')
        self._conn = S3Connection(key, secret, kw.get('secure', False))
        buckets = self._conn.get_all_buckets()
        # Use bucket if it exists
        for b in buckets:
            if b.name == bucket: 
                self._store = b
                break
        # Create bucket if it doesn't exist
        else:
            self._store = self._conn.create_bucket(bucket)
            self._store.set_acl(kw.get('acl', 'private'))
        # Flag to use compression
        self._compressed = kw.get('compressed', False)

    def __getitem__(self, key):
        rkey = self._store.lookup(key)
        if rkey is None: raise KeyError('%s' % key)
        # Fetch string
        value = self.loads(rkey.get_contents_as_string())
        # Flag that the store has not been updated
        self._updated = False
        return value

    def __setitem__(self, key, value):
        rkey = Key(self._store)
        rkey.key = key
        rkey.set_contents_from_string(self.dumps(value))
        # Flag that the store has been updated
        self._updated = True

    def __delitem__(self, key):
        try:
            self._store.delete_key(key)
            # Flag that the store has been updated
            self._updated = True
        except:
            raise KeyError('%s' % key)

    def keys(self):
        '''Returns a list of keys in the store.'''
        return list(i[0] for i in self.items())
    
    def items(self):
        '''Returns a list of items from the store.'''
        if self._updated or self._keys is None:
            self._keys = self._store.get_all_keys()
        return list((str(k.key), k) for k in self._keys)

    def iteritems(self):
        '''Lazily returns items from the store.'''
        for k in self.items(): yield (k.key, k)