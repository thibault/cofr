import os
import shutil
import json
from binascii import hexlify, unhexlify
from collections import MutableMapping
from tempfile import mkstemp
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from trezorlib.client import TrezorClient
from trezorlib.device import TrezorDevice


AES_IV_LENGTH = 12
AES_TAG_LENGTH = 16


def aes_gcm_encrypt(key, data):
    iv = os.urandom(AES_IV_LENGTH)
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    result = iv + encryptor.tag + ciphertext
    return result


def aes_gcm_decrypt(key, data):
    iv = data[:AES_IV_LENGTH]
    tag = data[AES_IV_LENGTH:AES_IV_LENGTH + AES_TAG_LENGTH]
    ciphertext = data[AES_IV_LENGTH + AES_TAG_LENGTH:]
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend())
    decryptor = cipher.decryptor()
    text = decryptor.update(ciphertext) + decryptor.finalize()
    return text


class EncryptedStore(MutableMapping):
    """An AES encrypted filebased mapping type.

    Instead of using the Trezor for encrypting the entire file (which could
    take some time), we use it to only generate an encryption key. Then, the
    file is encrypted / decrypted using a symmetric encryption algorithm (AES).
    """

    BIP_ADDRESS = "m/10016'/0"
    STORE_VERSION = '1'
    MASTER_ENC_KEY = 'Unlock file?'
    MASTER_ENC_VAL = b'\x8dX\xd4\xab\xact\x129=U\xce\xe2b\x93\x18\x80'
    ITEM_NONCE_SIZE = 32

    def __init__(self, filename):
        """Initialize the structure."""

        self.filename = filename
        self.master_key = self._generate_master_key()
        self.synced = True

        if os.path.exists(self.filename):
            self._dict = self._parse_file()
        else:
            self._dict = {
                'version': self.STORE_VERSION,
                'entries': {},
            }

    def _generate_master_key(self):
        """Returns the key for aes file encryption."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        key = hexlify(trezor.encrypt_keyvalue(
            address_n, self.MASTER_ENC_KEY, self.MASTER_ENC_VAL,
            ask_on_encrypt=True, ask_on_decrypt=True))

        return key

    def _parse_file(self):
        """Open and parse the file."""

        with open(self.filename, 'rb') as f:
            data = f.read()

        key = unhexlify(self.master_key)
        json_data = aes_gcm_decrypt(key, data).decode()
        return json.loads(json_data)

    def sync(self):
        """Write data content back to the file."""

        key = unhexlify(self.master_key)
        json_data = json.dumps(self._dict).encode()
        ciphertext = aes_gcm_encrypt(key, json_data)

        fd, tmpfile = mkstemp()
        with open(tmpfile, 'wb') as f:
            f.write(ciphertext)
        os.close(fd)

        shutil.move(tmpfile, self.filename)
        self.synced = True

    def close(self):
        """Close the file and make it unaccessible."""

        self._dict = None

    @property
    def closed(self):
        """True if the file was already synced and closed."""

        return self._dict is None

    def __setitem__(self, key, value):
        u"""Encrypt and stores a value in a file."""

        encrypted_nonce, encrypted_value = self.encrypt_item(
            key, value.encode())
        self._dict['entries'][key] = {
            'nonce': encrypted_nonce.decode(),
            'value': encrypted_value.decode()
        }
        self.synced = False

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        encrypted_nonce = self._dict['entries'][key]['nonce'].encode()
        encrypted_value = self._dict['entries'][key]['value'].encode()

        value = self.decrypt_item(
            key,
            encrypted_nonce,
            encrypted_value)
        return value.decode()

    def __delitem__(self, key):
        del self._dict['entries'][key]
        self.synced = False

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

    def encrypt_item(self, key, value):
        u"""Encrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        nonce = os.urandom(self.ITEM_NONCE_SIZE)
        nonce_key = 'Decrypt key {}?'.format(key)
        encrypted_nonce = trezor.encrypt_keyvalue(
            address_n, nonce_key, nonce, ask_on_encrypt=False,
            ask_on_decrypt=True)
        encrypted_value = aes_gcm_encrypt(nonce, value)

        trezor.close()
        return hexlify(encrypted_nonce), hexlify(encrypted_value)

    def decrypt_item(self, key, encrypted_nonce, encrypted_value):
        u"""Decrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        nonce_key = 'Decrypt key {}?'.format(key)
        nonce = bytes(trezor.decrypt_keyvalue(
            address_n, nonce_key, unhexlify(encrypted_nonce),
            ask_on_encrypt=False, ask_on_decrypt=True))
        value = aes_gcm_decrypt(nonce, unhexlify(encrypted_value))

        trezor.close()
        return value
