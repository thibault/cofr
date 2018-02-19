import shelve
import binascii
from collections import MutableMapping

from trezorlib.client import TrezorClient
from trezorlib.device import TrezorDevice


class KeyVal(MutableMapping):
    u"""A basic key: value persisting store, encrypted with a Trezor device.

    For storing data, we just use the `shelve` python standard library.

    Keys are stored plaintext, only values are encoded.
    """

    BIP_ADDRESS = "m/10016'/0"
    PAD_CHARACTER = b'\x80'  # unicode padding character

    def __init__(self, db_path):
        self.store = shelve.open(db_path)

    def find_trezor(self):
        u"""Selects a trezor device and initialize the client."""

        devices = TrezorDevice.enumerate()
        if len(devices) == 0:
            raise RuntimeError("No Trezor device was found.")

        transport = devices[0]
        trezor = TrezorClient(transport)
        return trezor

    def __getitem__(self, key):
        u"""Get a value from the store and return the decoded value."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        try:
            encrypted_value = binascii.unhexlify(self.store[key])
            decrypted_value = trezor.decrypt_keyvalue(
                address_n, key, encrypted_value)
            pad_index = decrypted_value.find(self.PAD_CHARACTER)
            value = decrypted_value[0:pad_index].decode('utf-8')
        except KeyError:
            value = None
        except binascii.Error:
            raise RuntimeError('The value is not correct hexadecimal data.')
        finally:
            trezor.close()

        return value

    def __setitem__(self, key, value):
        u"""Encrypt and stores a value in a file."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        # The value's length must be a multiple of 16.
        # Hence, we might have to pad the value.
        encoded = value.encode()
        pad_length = 16 - (len(encoded) % 16)
        padded_value = encoded + (self.PAD_CHARACTER * pad_length)
        encrypted_value = trezor.encrypt_keyvalue(address_n, key, padded_value)
        self.store[key] = binascii.hexlify(encrypted_value)

        trezor.close()

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
