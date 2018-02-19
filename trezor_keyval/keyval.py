import shelve
from collections import MutableMapping

from trezor_keyval.encoder import get_encoder


ENCODER = 'Trezor'


class KeyVal(MutableMapping):
    u"""A basic key: value persisting store, encrypted with a Trezor device.

    For storing data, we just use the `shelve` python standard library.

    Keys are stored plaintext, only values are encoded.
    """

    def __init__(self, db_path):
        self.store = shelve.open(db_path)
        self.encoder = get_encoder(ENCODER)

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        try:
            encrypted_value = self.store[key]
            value = self.encoder.decrypt(key, encrypted_value).decode('utf-8')
        except KeyError:
            value = None

        return value

    def __setitem__(self, key, value):
        u"""Encrypt and stores a value in a file."""

        encrypted_value = self.encoder.encrypt(key, value.encode('utf-8'))
        self.store[key] = encrypted_value

    def __delitem__(self, key):
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
