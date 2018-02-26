from trezor_keyval.encoder import pad_pkcs7, unpad_pkcs7


def test_pad_pkcs7():
    u"""Check the validity of the padding algorithm."""

    assert pad_pkcs7(b'testing', 8) == b'testing\x01'
    assert pad_pkcs7(b'toto', 8) == b'toto\x04\x04\x04\x04'
    assert pad_pkcs7(b'totototo', 8) == \
        b'totototo\x08\x08\x08\x08\x08\x08\x08\x08'
    assert pad_pkcs7(b'toto', 16) == \
        b'toto\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c'


def test_unpad_pkcs7():
    u"""check the validity of the unpad algorithm."""

    assert unpad_pkcs7(b'testing\x01') == b'testing'
    assert unpad_pkcs7(b'toto\x04\x04\x04\x04') == b'toto'
    assert unpad_pkcs7(
        b'totototo\x08\x08\x08\x08\x08\x08\x08\x08') == b'totototo'
    assert unpad_pkcs7(
        b'toto\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c') == b'toto'
