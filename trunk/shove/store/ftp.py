import urlparse
try:
    from cStringIO import StringIO
except ImportError:
    from cStringIO import StringIO
try:
    import cPickle as pickle
except ImportError:
    import pickle
from ftplib import FTP, error_perm
from shove import BaseStore

__all__ = ['FtpStore']


def FtpStore(BaseStore):

    def __init__(self, engine, **kw):
        super(FtpStore, self).__init__()
        spliturl = urlparse.urlsplit(engine)
        # Set URL, path, and strip 'ftp://' off
        base, path = spliturl[1], '/'.join([spliturl[2], ''])
        user = kw.get('user', 'anonymous')
        password = kw.get('password', '')
        self._store = FTP(base, user, password)
        # Change to remote path if it exits
        try:
            self._store.cwd(path)
        except error_perm:
            self._makedir(path)
        self._base, self._user, self._password = base, user, password
        self._updated, self._keys = True, None

    def __getitem__(self, key):
        try:
            local = StringIO()
            self._store.retrbinary('RETR %s' % key, local.write)
            value = pickle.load(local)
            self._updated = False
            return value
        except:
            raise KeyError()

    def __setitem__(self, key, value):
        local = StringIO()
        pickle.dump(value, local, 2)
        self._store.storbinary('STOR %s' % key, local)
        self._updated = True

    def __delitem__(self, key):
        self._store.delete(key)
        self._updated = True

    def _makedir(self, path):
        paths = list(reversed([i for i in path.split('/') if i != '']))
        while paths:
            tpath = paths.pop()
            self._store.mkd(tpath)
            self._store.cwd(tpath)

    def keys(self):        
        def sortftp(rdir):
            nlist = []
            for rl in rdir:
                # Split remote file based on whitespace
                ri = rl.split()
                # Append tuple of remote item type & name
                if ri[-1] not in ('.', '..'):
                    nlist.append((ri[0], ri[-1]))
            return nlist
        if not self._updates or self._keys is not None:
            return self._keys
        else:
            rlist = list()
            self._store.retrlines('LIST -a', rlist.append)
            return list(u for u in sortftp(rlist) if u[0] == '-')