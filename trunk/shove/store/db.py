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

'''Database object store.


The shove psuedo-URL used for database object stores is the format used by
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

try:
    from sqlalchemy import *
except ImportError:
    raise ImportError('DbCache cache requires the SQLAlchemy package.')
from shove import BaseStore

__all__ = ['DbStore']


class DbStore(BaseStore):     

    '''Database cache backend.'''

    def __init__(self, engine, **kw):
        super(DbStore, self).__init__(**kw)
        # Bind metadata
        self._metadata = BoundMetaData(engine)
        # Get tablename
        tablename = kw.get('tablename', 'store')
        # Make store table
        self._store = Table(tablename, self._metadata,
            Column('store_key', String(256), primary_key=True,
                nullable=False),
            Column('store_value', Binary, nullable=False))
        # Create store table if it does not exist
        if not self._store.exists(): self._store.create()

    def __getitem__(self, key):
        row = self._store.select().execute(store_key=key).fetchone()
        if row is not None:
            return self.loads(str(row.store_value))
        raise KeyError('Key "%s" not found.' % key)
        
    def __setitem__(self, key, value):
        value = self.dumps(value)
        # Update database if key already present
        if key in self:
            self._store.update(
                self._store.c.store_key==key).execute(store_value=value)
        # Insert new key if key not present
        else:            
            self._store.insert().execute(store_key=key, store_value=value)
       
    def __delitem__(self, key):
        self._store.delete(self._store.c.store_key==key).execute()

    def keys(self):
        '''Returns a list of keys in the store.'''
        return list(i[0] for i in select(
            [self._store.c.store_key]).execute().fetchall())