# Copyright (c) 2005, the Lawrence Journal-World
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

'''Database store.'''

try:
    from sqlalchemy import *
except ImportError:
    raise ImportError('DbCache module requires the SQLAlchemy package ' \
        'from http://www.sqlalchemy.org/')
from shove import BaseStore

__all__ = ['DbStore']   


class DbStore(BaseStore):     

    '''Database cache backend.'''

    def __init__(self, *a, **kw):
        super(DbStore, self).__init__(self, *a, **kw)
        # Bind metadata
        self._metadata = BoundMetaData(a[0])
        # Make cache
        self._store = Table('store', self._metadata,
            Column('store_key', String(256), primary_key=True, nullable=False, unique=True),
            Column('store_value', PickleType, nullable=False))
        # Create cache if it does not exist
        if not self._store.exists(): self._store.create()

    def __getitem__(self, key):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        '''
        row = self._store.select().execute(store_key=key).fetchone()
        if row is not None: return row.store_value
        raise KeyError()        
        
    def __setitem__(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.        
        '''
        # Update database if key already present
        if key in self:
            self._store.update(self._store.c.store_key==key).execute(store_value=value)
        # Insert new key if key not present
        else:            
            self._store.insert().execute(store_key=key, store_value=value)
       
    def __delitem__(self, key):
        '''Delete a key from the cache, failing silently.

        @param key Keyword of item in cache.
        '''
        self._store.delete().execute(store_key=key)

    def keys(self):
        return list(i[0] for i in select([self._store.c.store_key]).execute().fetchall())