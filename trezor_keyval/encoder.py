import abc
import binascii
import base64

from trezorlib.client import TrezorClient
from trezorlib.device import TrezorDevice


class BaseEncoder(abc.ABC):
    u"""Defines the interface for encoder classes."""

    @abc.abstractmethod
    def encrypt(self, key, value):
        u"""Encrypt a given value.

        The value must be a binary string (bytes).
        """

        pass

    @abc.abstractmethod
    def decrypt(self, key, encrypted_value):
        u"""Decrypt a given value.

        Returns a binary (bytes) string.
        """

        pass


class DummyEncoder(BaseEncoder):
    u"""Uses base64 to fake encryption / decryption data.

    This is useful to run tests, when no hardware device is present.
    """

    def encrypt(self, key, value):
        return base64.b64encode(value)

    def decrypt(self, key, encrypted_value):
        return base64.b64decode(encrypted_value)


class TrezorEncoder(BaseEncoder):
    u"""Use a connected Trezor to encrypt / decrypt data."""

    BIP_ADDRESS = "m/10016'/0"
    PAD_CHARACTER = b'\x80'  # unicode padding character

    def find_trezor(self):
        u"""Selects a trezor device and initialize the client."""

        devices = TrezorDevice.enumerate()
        if len(devices) == 0:
            raise RuntimeError("No Trezor device was found.")

        transport = devices[0]
        trezor = TrezorClient(transport)
        return trezor

    def decrypt(self, key, encrypted_value):
        u"""Decrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        decrypted_value = trezor.decrypt_keyvalue(
            address_n, key, encrypted_value)
        pad_index = decrypted_value.find(self.PAD_CHARACTER)
        try:
            value = binascii.unhexlify(decrypted_value[0:pad_index])
        except binascii.Error:
            raise RuntimeError('The value is not correct hexadecimal data.')
        finally:
            trezor.close()

        return value

    def encrypt(self, key, value):
        u"""Encrypt the given value using the connected Trezor."""

        trezor = self.find_trezor()
        address_n = trezor.expand_path(self.BIP_ADDRESS)

        # The value's length must be a multiple of 16.
        # Hence, we might have to pad the value.
        pad_length = 16 - (len(value) % 16)
        padded_value = value + (self.PAD_CHARACTER * pad_length)
        encrypted_value = binascii.hexlify(
            trezor.encrypt_keyvalue(address_n, key, padded_value))
        trezor.close()

        return encrypted_value


def get_encoder(strategy):
    u"""Returns an initialized encoder."""

    strategies = {
        'Trezor': TrezorEncoder,
        'Dummy': DummyEncoder,
    }
    Encoder = strategies.get(strategy, None)
    if Encoder is None:
        raise RuntimeError('Unknown encoder required')

    return Encoder()
