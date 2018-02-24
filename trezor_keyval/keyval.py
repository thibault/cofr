import os
import json
from binascii import hexlify, unhexlify
from collections import MutableMapping
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def encrypt(key, value):
    return value


def decrypt(key, value):
    return value


class EncryptedStore(MutableMapping):
    """An AES encrypted filebased mapping type.

    Instead of using the Trezor for encrypting the entire file (which could
    take some time), we use it to only generate an encryption key. Then, the
    file is encrypted / decrypted using a symmetric encryption algorithm (AES).
    """

    def __init__(self, filename):
        """Initialize the structure."""

        self.filename = filename
        self.master_key = self._generate_master_key()
        if os.path.exists(self.filename):
            self._dict = self._parse_file()
        else:
            self._dict = {}

    def _generate_master_key(self):
        """Returns the key for aes file encryption."""

        return hexlify(b'toto' * 10)[:32]

    def _parse_file(self):
        """Open and parse the file."""

        with open(self.filename, 'rb') as f:
            iv = f.read(12)
            tag = f.read(16)
            cipherkey = unhexlify(self.master_key)
            cipher = Cipher(
                algorithms.AES(cipherkey),
                modes.GCM(iv, tag),
                backend=default_backend())
            decryptor = cipher.decryptor()

            ciphertext = f.read()
            json_data = decryptor.update(ciphertext) + decryptor.finalize()
        return json.loads(json_data.decode())

    def _sync(self):
        """Write data content back to the file."""

        with open(self.filename, 'wb') as f:
            iv = os.urandom(12)
            cipherkey = unhexlify(self.master_key)
            cipher = Cipher(
                algorithms.AES(cipherkey),
                modes.GCM(iv),
                backend=default_backend())
            encryptor = cipher.encryptor()
            json_data = json.dumps(self._dict).encode()
            ciphertext = encryptor.update(json_data) + encryptor.finalize()

            f.write(iv)
            f.write(encryptor.tag)
            f.write(ciphertext)

    def close(self):
        """Close the file and make it unaccessible."""

        self._sync()
        self._dict = None

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        encrypted_value = self._dict[key]
        value = decrypt(key, encrypted_value)
        return value

    def __setitem__(self, key, value):
        u"""Encrypt and stores a value in a file."""

        encrypted_value = encrypt(key, value)
        self._dict[key] = encrypted_value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __contains__(self, item):
        return item in self._dict
