import pytest
from cofr.store import BaseEncryptedStore


@pytest.fixture
def store_data():
    return {
        'version': 1,
        'entries': {
            'toto': {
                'nonce': '',
                'value': '746f746f',  # "toto" hexlified
            },
            'tata': {
                'nonce': '',
                'value': '74617461',   # "tata" hexlified
            }
        }
    }


@pytest.fixture(scope='module')
def store_file(tmpdir):
    pass


def test_store_getitem(tmpdir, store_data):
    """Test that the __getitem__ method works."""

    filename = tmpdir.join('void.db')
    store = BaseEncryptedStore(filename)
    store._dict = store_data

    assert store['toto'] == 'toto'


def test_getitem_with_unexisting_key(tmpdir, store_data):
    """Getting a key that does not exist raises an exception."""

    filename = tmpdir.join('void.db')
    store = BaseEncryptedStore(filename)
    store._dict = store_data

    with pytest.raises(KeyError):
        store['camembert']


def test_store_setitem(tmpdir):
    """Test that the __setitem__ method works."""

    filename = tmpdir.join('void.db')
    store = BaseEncryptedStore(filename)
    store['toto'] = 'toto'

    assert store['toto'] == 'toto'


def test_store_can_override_existing_key(tmpdir):
    """Test that it's possible to override an existing key."""

    filename = tmpdir.join('void.db')
    store = BaseEncryptedStore(filename)
    store['toto'] = 'toto'
    store['toto'] = 'tata'

    assert store['toto'] == 'tata'


def test_store_contains(tmpdir):
    """Test the __contains__ method."""

    filename = tmpdir.join('void.db')
    store = BaseEncryptedStore(filename)
    assert 'toto' not in store

    store['toto'] = 'tata'
    assert 'toto' in store


def test_del_key(tmpdir):
    """Test the __delitem__ method."""

    filename = tmpdir.join('void.db')
    store = BaseEncryptedStore(filename)
    store['toto'] = 'tata'
    del store['toto']
    assert 'toto' not in store


def test_store_sync_to_disk(tmpdir):
    """Write the store content to disk."""

    filename = tmpdir.join('void.db')
    assert not filename.check()

    store = BaseEncryptedStore(filename)
    store['toto'] = 'toto'
    store['tata'] = 'tata'
    store.sync()
    store.close()
    assert filename.check()

    new_store = BaseEncryptedStore(filename)
    assert new_store['toto'] == 'toto'
    assert new_store['tata'] == 'tata'
