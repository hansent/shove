# Copyright (c) 2005, the Lawrence Journal-World
# Copyright (c) 2011 L. C. Rees
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

'''Cassandra-based object store

The shove psuedo-URL for a cassandra-based store is:

cassandra://<host>:<port>/<keyspace>/<columnFamily>
'''

import urlparse

try:
    import pycassa
except ImportError:
    raise ImportError('This store requires the pycassa library')

from shove import BaseStore

__all__ = ['CassandraStore']


class CassandraStore(BaseStore):

    '''Cassandra based store'''

    init = 'cassandra://'

    def __init__(self, engine, **kw):
        super(CassandraStore, self).__init__(engine, **kw)
        spliturl = urlparse.urlsplit(engine)
        _, keyspace, column_family = spliturl[2].split('/')
        try:
            self._pool = pycassa.connect(keyspace, [spliturl[1]])
            self._store = pycassa.ColumnFamily(self._pool, column_family)
        except pycassa.InvalidRequestException:
            from pycassa.system_manager import SystemManager
            system_manager = SystemManager(spliturl[1])
            system_manager.create_keyspace(
                keyspace, kw.get('replication', 1)
            )
            system_manager.create_column_family(keyspace, column_family)
            self._pool = pycassa.connect(keyspace, [spliturl[1]])
            self._store = pycassa.ColumnFamily(self._pool, column_family)

    def __getitem__(self, key):
        try:
            item = self._store.get(key).get(key)
            if item is not None: return self.loads(item)
            raise KeyError('%s'%key)
        except pycassa.NotFoundException:
            raise KeyError('%s'%key)

    def __setitem__(self, key, value):
        self._store.insert(key, dict(key=self.dumps(value)))

    def __delitem__(self, key):
        # beware eventual consistency
        try:
            self._store.remove(key)
        except pycassa.NotFoundException:
            raise KeyError('%s'%key)

    def clear(self):
        # beware eventual consistency
        self._store.truncate()

    def keys(self):
        return list(i[0] for i in self._store.get_range())
