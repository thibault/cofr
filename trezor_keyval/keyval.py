from shelve import Shelf
import os
from collections import MutableMapping

from trezor_keyval.encoder import get_encoder


ENCODER = 'Trezor'


def encrypt(key, value):
    return value


def decrypt(key, value):
    return value


class EncryptedDict(MutableMapping):
    """An AES encrypted filebased mapping type."""

    def __init__(self, filename):
        """Initialize the structure."""

        self.filename = filename
        if not os.path.exists(self.filename):
            self._create()
        self._open()

    def _create(self):
        """Creates a new encrypted file."""
        pass

    def _open(self):
        """Open and parse the file."""
        pass

    def sync(self):
        """Write data content back to the file."""
        pass

    def close(self):
        """Close the file and make it unaccessible."""
        self.sync()
        self._dict = None

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len(self):
        return len(self._dict)

    def __contains__(self, item):
        return item in self._dict


class EncryptedShelf(Shelf):
    """A shelf interface with encryption.

    We provide two levels of encryption:
     - first, every key is encrypted before being stored
     - second, the file itself is encrypted.

    """

    def __init__(self, filename):
        writeback = True  # only write file when closing the store.
        encrypted_dict = EncryptedDict(filename)
        super().__init__(self, encrypted_dict, writeback=writeback)

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        encrypted_value = super().__getitem__(key)
        value = decrypt(key, encrypted_value).decode('utf-8')
        return value

    def __setitem__(self, key, value):
        u"""Encrypt and stores a value in a file."""

        encrypted_value = encrypt(key, value.encode('utf-8'))
        super().__setitem__(key, encrypted_value)


class KeyVal(MutableMapping):
    u"""A basic key: value persisting store, encrypted with a Trezor device.

    For storing data, we just use the `shelve` python standard library.

    Keys are stored plaintext, only values are encoded.
    """

    def __init__(self, db_path):
        self.db_path = db_path
        # self.store = shelve.open(db_path)
        self.encoder = get_encoder(ENCODER)

    def db_exists(self):
        u"""Checks that the db path already exists."""

        return os.path.exists(self.db_path)

    def initialize_db(self):
        u"""Create an empty db file."""

        pass

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        try:
            encrypted_value = self.store[key]
            value = self.encoder.decrypt(key, encrypted_value).decode('utf-8')
        except KeyError:
            value = u''

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

    def get_encrypted_value(self, key):
        u"""Return the value as it is stored, without decryption."""

        try:
            encrypted_value = self.store[key].decode()
        except KeyError:
            encrypted_value = u''

        return encrypted_value

    def keys(self):
        return list(self.store.keys())

    def close(self):
        self.store.close()
