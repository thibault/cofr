import os
import json
from binascii import hexlify, unhexlify, Error as BinASCIIError
from collections import MutableMapping
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from trezorlib.client import TrezorClient
from trezorlib.device import TrezorDevice


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

    BIP_ADDRESS = "m/10016'/0"
    STORE_VERSION = '1'

    def __init__(self, filename):
        """Initialize the structure."""

        self.filename = filename
        self.master_key = self._generate_master_key()
        self.writeback = False

        if os.path.exists(self.filename):
            self._dict = self._parse_file()
        else:
            self._dict = {
                'version': self.STORE_VERSION,
                'entries': {},
            }

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

        if self.writeback:
            self._sync()
        self._dict = None

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        encrypted_value = self._dict['entries'][key]
        value = self.decrypt_item(key, encrypted_value).decode()
        return value

    def __setitem__(self, key, value):
        u"""Encrypt and stores a value in a file."""

        encrypted_value = self.encrypt_item(key, value.encode())
        self._dict['entries'][key] = encrypted_value
        self.writeback = True

    def __delitem__(self, key):
        del self._dict['entries'][key]
        self.writeback = True

    def __iter__(self):
        return iter(self._dict['entries'])

    def __len__(self):
        return len(self._dict['entries'])

    def __contains__(self, item):
        return item in self._dict['entries']

    def find_trezor(self):
        u"""Selects a trezor device and initialize the client."""

        devices = TrezorDevice.enumerate()
        if len(devices) == 0:
            raise RuntimeError("No Trezor device was found.")

        transport = devices[0]
        trezor = TrezorClient(transport)
        return trezor

    def decrypt_item(self, key, encrypted_value):
        u"""Decrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)
        unpadder = PKCS7(16 * 8).unpadder()

        try:
            decrypted_value = trezor.decrypt_keyvalue(
                address_n, key, unhexlify(encrypted_value))
            value = unpadder.update(decrypted_value) + unpadder.finalize()
        except BinASCIIError:
            raise RuntimeError('The value is not correct hexadecimal data.')
        finally:
            trezor.close()

        return value

    def encrypt_item(self, key, value):
        u"""Encrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)
        padder = PKCS7(16 * 8).padder()
        nonce = hexlify(os.urandom(32))
        key = 'Decrypt key {}?'.format(key)
        cipherkey = trezor.encrypt_keyvalue(
            address_n, key, nonce, ask_on_encrypt=False, ask_on_decrypt=True)

        # The value's length must be a multiple of 16.
        # Hence, we might have to pad the value.
        padded_value = padder.update(value) + padder.finalize()
        encrypted_value = hexlify(
            trezor.encrypt_keyvalue(address_n, key, padded_value))
        trezor.close()

        return encrypted_value
