import pytest
from unittest import mock
from click.testing import CliRunner

from cofr.cli import cli, CofrShell


@pytest.fixture
def store():
    return {
        'fromage': 'camembert',
        'plat': 'tartiflette',
    }


@pytest.fixture
def runner():
    return CliRunner()


def test_missing_command(runner):
    """The filepath argument is mandatory."""

    result = runner.invoke(cli)
    assert result.exit_code == 2
    assert result.output.startswith('Usage:')


def test_list_keys(store, capsys):
    """Check that all keys are displayed."""

    shell = CofrShell(store=store)
    shell.do_list('')
    captured = capsys.readouterr()

    assert captured.out == 'Here is the list of all known items:\n' \
        ' - fromage\n - plat\n'


def test_get_existing_key(store, capsys):
    """Check that it's possible to view an existing key."""

    shell = CofrShell(store=store)
    shell.do_get('plat')
    captured = capsys.readouterr()

    assert 'tartiflette' in captured.out


def test_get_unknown_key(store, capsys):
    """Check that getting an unknown display a nice message."""

    shell = CofrShell(store=store)
    shell.do_get('acteur')
    captured = capsys.readouterr()

    assert 'There is no such key' in captured.out


def test_set_new_key(store, capsys, monkeypatch):
    """Setting a new key records it's value."""

    shell = CofrShell(store=store)

    monkeypatch.setattr('cofr.cli.click.prompt', lambda x: 'Jacques Villeret')
    shell.do_put('acteur')
    captured = capsys.readouterr()

    assert 'Done!' in captured.out
    assert store['acteur'] == 'Jacques Villeret'


def test_set_existing_key(store, capsys, monkeypatch):
    """Setting an existing key is forbidden."""

    shell = CofrShell(store=store)

    monkeypatch.setattr('cofr.cli.click.prompt', lambda x: 'reblochon')
    shell.do_put('fromage')
    captured = capsys.readouterr()

    assert 'For safety reasons' in captured.out
    assert store['fromage'] == 'camembert'


def test_del_key(store, monkeypatch):
    """Testing the removal of a key."""

    shell = CofrShell(store=store)
    assert 'fromage' in store

    monkeypatch.setattr('cofr.cli.click.confirm', lambda x: 'y')
    shell.do_del('fromage')
    assert 'fromage' not in store


def test_quitting_when_synced(capsys):
    """Quitting when file is synced executes immediately."""

    store = mock.Mock()
    store.synced = True

    shell = CofrShell(store=store)

    with mock.patch('cofr.cli.click.confirm') as confirm:
        shell.do_quit('')
        captured = capsys.readouterr()
        assert not confirm.called
        assert 'Bye!' in captured.out


def test_quitting_before_syncing(capsys):
    """Quitting before syncing must display a warning."""

    store = mock.Mock()
    store.synced = False

    shell = CofrShell(store=store)

    with mock.patch('cofr.cli.click.confirm') as confirm:
        shell.do_quit('')
        captured = capsys.readouterr()
        assert confirm.called
        assert 'Bye!' not in captured.out
