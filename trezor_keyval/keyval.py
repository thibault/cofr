import shelve
from collections import MutableMapping


class KeyVal(MutableMapping):

    def __init__(self, db_path):
        self.store = shelve.open(db_path)

    def __getitem__(self, key):
        try:
            value = self.store[key]
        except KeyError:
            value = None
        return value

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        if key in self.store:
            del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __contains__(self, key):
        return key in self.store

    def keys(self):
        return list(self.store.keys())

    def close(self):
        self.store.close()
