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

from .exceptions import NoTrezorFoundError, InvalidCofrFileError


AES_IV_LENGTH = 12
AES_TAG_LENGTH = 16


def aes_gcm_encrypt(key, data, iv=None):
    """Encrypt data using AES with GCM mode.

    12 first bytes of the response are the initialization vector (iv).
    16 next bytes are the authentication tag.
    The rest is the encrypted text.
    """

    iv = iv or os.urandom(AES_IV_LENGTH)
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    result = iv + encryptor.tag + ciphertext
    return result


def aes_gcm_decrypt(key, data):
    """Decrypt AES-GCM encrypted data.

    Data must start with the iv and tag, as return in `aes_gcm_encrypt`.
    """

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


class BaseEncryptedStore(MutableMapping):
    """An AES encrypted filebased mapping type.

    Instead of using the Trezor for encrypting the entire file (which could
    take some time), we use it to only generate an encryption key. Then, the
    file is encrypted / decrypted using a symmetric encryption algorithm (AES).

    This base class MUST NOT be used directly. Allowing it to be instanciated
    makes testing easier, though.
    """

    BIP_ADDRESS = "m/10016'/0"
    STORE_VERSION = '1'
    MASTER_ENC_KEY = 'Decrypt Cofr file?'
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

        return self.MASTER_ENC_VAL

    def _parse_file(self):
        """Open and parse the file."""

        with open(self.filename, 'rb') as f:
            data = f.read()

        key = self.master_key
        try:
            json_data = aes_gcm_decrypt(key, data).decode()
        except ValueError:
            raise InvalidCofrFileError('The file content does not seem to be '
                                       'valid.')
        return json.loads(json_data)

    def sync(self):
        """Write data content back to the file."""

        key = self.master_key
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

        encrypted_nonce, encrypted_value = self.encrypt_item(key, value)
        self._dict['entries'][key] = {
            'nonce': hexlify(encrypted_nonce).decode(),
            'value': hexlify(encrypted_value).decode()
        }
        self.synced = False

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        encrypted_nonce = self._dict['entries'][key]['nonce'].encode()
        encrypted_value = self._dict['entries'][key]['value'].encode()

        value = self.decrypt_item(
            key,
            unhexlify(encrypted_nonce),
            unhexlify(encrypted_value))
        return value

    def __delitem__(self, key):
        del self._dict['entries'][key]
        self.synced = False

    def __iter__(self):
        return iter(self._dict['entries'])

    def __len__(self):
        return len(self._dict['entries'])

    def __contains__(self, item):
        return item in self._dict['entries']

    def encrypt_item(self, key, value):
        u"""Encrypt the given value."""

        return key.encode(), value.encode()

    def decrypt_item(self, key, encrypted_nonce, encrypted_value):
        u"""Decrypt the given value."""

        return encrypted_value.decode()


class TrezorEncryptedStore(BaseEncryptedStore):
    u"""Use the Trezor hardware wallet for encryption / decryption."""

    def _generate_master_key(self):
        """Returns the key for aes file encryption.

        To generate a unique and deterministic encryption key, we simply
        encrypt a constant value using the Trezor.
        """

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        key = bytes(trezor.encrypt_keyvalue(
            address_n, self.MASTER_ENC_KEY, self.MASTER_ENC_VAL,
            ask_on_encrypt=True, ask_on_decrypt=True))

        return key

    def find_trezor(self):
        u"""Selects a trezor device and initialize the client."""

        devices = TrezorDevice.enumerate()
        if len(devices) == 0:
            raise NoTrezorFoundError('No Trezor device was found. Make sure it'
                                     ' is plugged.')

        transport = devices[0]
        trezor = TrezorClient(transport)
        return trezor

    def encrypt_item(self, key, value):
        u"""Encrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        nonce = os.urandom(self.ITEM_NONCE_SIZE)
        nonce_key = 'Decrypt key {}?'.format(key)
        encrypted_nonce = bytes(trezor.encrypt_keyvalue(
            address_n, nonce_key, nonce, ask_on_encrypt=False,
            ask_on_decrypt=True))
        encrypted_value = aes_gcm_encrypt(nonce, value.encode())

        trezor.close()
        return encrypted_nonce, encrypted_value

    def decrypt_item(self, key, encrypted_nonce, encrypted_value):
        u"""Decrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        nonce_key = 'Decrypt key {}?'.format(key)
        nonce = bytes(trezor.decrypt_keyvalue(
            address_n, nonce_key, encrypted_nonce,
            ask_on_encrypt=False, ask_on_decrypt=True))
        value = aes_gcm_decrypt(nonce, encrypted_value)

        trezor.close()
        return value.decode()
