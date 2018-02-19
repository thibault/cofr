import shelve
import pytest
from click.testing import CliRunner

from trezor_keyval import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def shelf():
    return {
        'toto': b'tata',
        'tata': b'tutu'
    }


@pytest.fixture(autouse=True)
def use_dummy_encoder(monkeypatch):
    monkeypatch.setattr('trezor_keyval.keyval.ENCODER', 'Dummy')


def test_get_empty_key(runner):
    with runner.isolated_filesystem():
        with shelve.open('db') as db:
            db.sync()

        result = runner.invoke(cli.cli, ['--file=db', 'get', 'toto'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == ''


def test_get_existing_key(runner, shelf):
    with runner.isolated_filesystem():
        with shelve.open('db') as db:
            for key, val in shelf.items():
                db[key] = val

        result = runner.invoke(cli.cli, ['--file=db', 'get', 'toto'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == 'tata'


def test_set_key(runner):
    with runner.isolated_filesystem():
        with shelve.open('db') as db:
            db.sync()

        result = runner.invoke(cli.cli, ['--file=db', 'set', 'toto', 'tata'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == ''

        result = runner.invoke(cli.cli, ['--file=db', 'get', 'toto'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == 'tata'


def test_key_overriding_is_forbidden(runner, shelf):
    with runner.isolated_filesystem():
        with shelve.open('db') as db:
            for key, val in shelf.items():
                db[key] = val

        result = runner.invoke(cli.cli, ['--file=db', 'set', 'toto', 'tutu'])
        assert result.exit_code == 2
        assert result.exception
        assert 'cannot be overriden' in result.output

        result = runner.invoke(cli.cli, ['--file=db', 'get', 'toto'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == 'tata'


def test_rm_existing_key(runner, shelf):
    with runner.isolated_filesystem():
        with shelve.open('db') as db:
            for key, val in shelf.items():
                db[key] = val

        result = runner.invoke(cli.cli, ['--file=db', 'rm', 'toto', '--yes'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == ''

        result = runner.invoke(cli.cli, ['--file=db', 'get', 'toto'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == ''


def test_rm_non_existing_key(runner):
    with runner.isolated_filesystem():
        with shelve.open('db') as db:
            db.sync()

        result = runner.invoke(cli.cli, ['--file=db', 'rm', 'toto', '--yes'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == ''

        result = runner.invoke(cli.cli, ['--file=db', 'get', 'toto'])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == ''


def test_list_keys(runner, shelf):
    with runner.isolated_filesystem():
        with shelve.open('db') as db:
            for key, val in shelf.items():
                db[key] = val

        result = runner.invoke(cli.cli, ['--file=db', 'list'])
        assert result.exit_code == 0
        assert not result.exception
        assert 'toto' in result.output
        assert 'tata' in result.output
