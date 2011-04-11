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

'''Redis-based object store

The shove psuedo-URL for a redis-based store is:

redis://<host>:<port>/<db>
'''

import urlparse

try:
    import redis
except ImportError:
    raise ImportError('This store requires the redis library')

from shove.store.simple import SimpleStore

__all__ = ['RedisStore']


class RedisStore(SimpleStore):

    '''Redis based store'''

    init = 'redis://'

    def __init__(self, engine, **kw):
        super(RedisStore, self).__init__(engine, **kw)
        spliturl = urlparse.urlsplit(engine)
        host, port = spliturl[1].split(':')
        db = spliturl[2].replace('/', '')
        self._store = redis.Redis(host, int(port), db)

    def __getitem__(self, key):
        item = super(RedisStore, self).__getitem__(key)
        if item is not None: return item
        raise KeyError('%s' % key)