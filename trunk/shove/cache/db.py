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

'''Database object cache.


The shove psuedo-URL used for database object caches is the format used by
SQLAlchemy:

<driver>://<username>:<password>@<host>:<port>/<database>

<driver> is the database engine. The engines currently supported SQLAlchemy are
sqlite, mysql, postgres, oracle, mssql, and firebird.
<username> is the database account user name
<password> is the database accound password
<host> is the database location
<port> is the database port
<database> is the name of the specific database

For more information on specific databases see:

http://www.sqlalchemy.org/docs/dbengine.myt#dbengine_supported
'''

import time
import random
from datetime import datetime
try:
    from sqlalchemy import *
except ImportError:
    raise ImportError('DbCache module requires the SQLAlchemy package ' \
        'from http://www.sqlalchemy.org/')
from shove.cache import BaseCache

__all__ = ['DbCache']


class DbCache(BaseCache):

    '''Database cache backend.'''

    def __init__(self, engine, **kw):
        super(DbCache, self).__init__(**kw)
        # Get table name
        tablename = kw.get('tablename', 'cache')
        # Bind metadata
        self._metadata = BoundMetaData(engine)
        # Make cache table
        self._cache = Table(tablename, self._metadata,
            Column('cache_key', String(60), primary_key=True,
                nullable=False, unique=True),
            Column('value', Binary, nullable=False),
            Column('expires', DateTime, nullable=False))
        # Create cache table if it does not exist
        if not self._cache.exists(): self._cache.create()        
        self._max_entries = kw.get('max_entries', 300)
        # Maximum number of entries to cull per call if cache is full
        self._maxcull = kw.get('maxcull', 10)

    def __getitem__(self, key):
        row = self._cache.select().execute(cache_key=key).fetchone()
        # Remove if item expired
        if row.expires < datetime.now().replace(microsecond=0):
            del self[key]
            raise KeyError('%s' % key)
        return self.loads(row.value)

    def __setitem__(self, key, val):
        timeout = self.timeout
        val=self.dumps(val)
        # Cull if too many items
        if len(self) >= self._max_entries: self._cull()
        # Generate expiration time
        exp = datetime.fromtimestamp(
            time.time() + timeout).replace(microsecond=0)
        try:
            # Update database if key already present
            if key in self:
                self._cache.update(self._cache.c.cache_key==key).execute(
                    value=val, expires=exp)
            # Insert new key if key not present
            else:            
                self._cache.insert().execute(cache_key=key,
                    value=val, expires=exp)
        # To be threadsafe, updates/inserts are allowed to fail silently
        except: pass

    def __delitem__(self, key):
        self._cache.delete(self._store.c.store_key==key).execute()

    def __len__(self):
        return self._cache.count().execute().fetchone()[0]

    def _cull(self):
        '''Remove items in cache to make more room.'''
        # Remove items that have timed out
        now = datetime.now().replace(microsecond=0)
        self._cache.delete(self._cache.c.expires < now).execute()
        # Remove any items over the maximum allowed number in the cache
        if len(self) >= self._max_entries:
            keys = [i[0] for i
                in select([self._cache.c.store_key]).execute().fetchall()]
            delkeys = list(random.choice(keys) for i in range(self._maxcull))
            self._cache.delete(self._cache.c.cache_key.like(
                bindparam('key'))).execute(*tuple({
                    'key':'%' + key + '%'} for key in delkeys))