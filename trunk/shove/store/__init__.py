from shove.store.simple import SimpleStore

__all__ = ['SyncStore', 'atom', 'bsddb', 'db', 'durus',
    'file', 'ftp', 'memory', 's3', 'simple', 'svn', 'zodb']


class BaseStore(Base):

    '''Base Store.'''
    
    def __init__(self):
        super(BaseStore, self).__init__()

    def keys(self):
        raise NotImplementedError()

    def __iter__(self):
        for k in self.keys(): yield k

    def iteritems(self):
        for k in self: yield (k, self[k])
            
    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        for _, v in self.iteritems(): yield v
        
    def values(self):
        return [v for _, v in self.iteritems()]
    
    def items(self):
        return list(self.iteritems())
    
    def clear(self):
        for key in self.keys(): del self[key]
        
    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError('pop expected at most 2 arguments, got '\
                + repr(1 + len(args)))
        try:
            value = self[key]
        except KeyError:
            if args: return args[0]
            raise
        del self[key]
        return value

    def popitem(self):
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError('container is empty')
        del self[k]
        return (k, v)

    def update(self, other=None, **kw):
        # Make progressively weaker assumptions about "other"
        if other is None:
            pass
        elif hasattr(other, 'iteritems'):  
            for k, v in other.iteritems():
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys():
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v
        if kw:
            self.update(kw)

    def __repr__(self):
        return repr(dict(self.iteritems()))

    def __cmp__(self, other):
        if other is None: return False
        if isinstance(other, BaseStore): other = dict(other.iteritems())
        return cmp(dict(self.iteritems()), other)

    def __len__(self):
        return len(self.keys())

    def __del__(self):
        # __init__ didn't succeed, so don't bother closing
        if not hasattr(self, '_store'): return
        self.close()    

    def close(self):
        try:
            self._store.close()
        except AttributeError: pass
        self._store = None


class SyncStore(SimpleStore):

    def __init__(self, engine, **kw):
        super(SyncStore, self).__init__(engine, **kw)

    def __setitem__(self, key, value):        
        super(SyncStore, self).__setitem__(key, value)
        self.sync()

    def __delitem__(self, key):
        super(SyncStore, self).__delitem__(key)
        self.sync()