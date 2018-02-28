import os
import errno
import cmd
import click

from .store import TrezorEncryptedStore
from .exceptions import NoTrezorFoundError, InvalidCofrFileError


class CofrShell(cmd.Cmd):
    prompt = 'Cofr> '
    intro = """
Welcome to the Cofr shell. Type help or ? for command list.

This software comes with NO WARRANTY whatsoever. Use it at your own risk.
Make sure to **backup** your store file.
    """

    def __init__(self, *args, **kwargs):
        self.store = kwargs.pop('store')
        super().__init__(*args, **kwargs)

    def emptyline(self):
        """Do nothing, don't repeat previous command."""
        pass

    def do_list(self, arg):
        """List all available keys in the store file."""

        click.echo('Here is the list of all known items:')
        for key in self.store:
            click.echo(' - {}'.format(key))

    def do_get(self, arg):
        """Decrypt and display a value from the store."""

        if arg == '':
            click.echo('Please, provide the key name to display.')
            return

        key = arg
        if key in self.store:
            click.echo('Please, confirm key decryption on the device.')
            value = self.store[key]
            click.echo(value)
        else:
            click.echo('There is no such key.')

    def do_put(self, arg):
        """Encrypt and save a value into the store."""

        if arg == '':
            click.echo('Please, provide the key name to set.')
            return

        key = arg
        if key in self.store:
            click.echo(
                'For safety reasons, existing keys cannot be modified.\n'
                'Remove it first then create it anew.')
        else:
            value = click.prompt('Please, provide the value for key'
                                 ' "{}"'.format(key))
            self.store[key] = value
            click.echo('Done!')

    def do_del(self, arg):
        """Removes an existing value from the store."""

        if arg == '':
            click.echo('Please, provide the key name to delete.')
            return

        key = arg
        if key in self.store:
            if click.confirm('Are you sure you want drop that key?'):
                del self.store[key]
        else:
            click.echo('There is no such key.')

    def do_sync(self, arg):
        """Writes data back to the disk."""

        if self.store.synced:
            click.echo('No changes were done, there is nothing to write.')
        else:
            self.store.sync()
            click.echo('Changes written back to disk.')

    def do_quit(self, arg):
        """Exits the shell."""

        if self.store.synced:
            click.echo('Bye!')
            return True
        else:
            return click.confirm(
                'The store was modified but not synced to disk. If you exit '
                'now, all your changes will be lost.\n\nAre you sure you want '
                'to continue?')
    do_q = do_quit
    do_exit = do_quit

    def postloop(self):
        self.store.close()


@click.command()
@click.option('-f', '--filepath', required=True, type=click.Path(
    readable=True, writable=True, dir_okay=False, resolve_path=True))
def cli(filepath):
    """Script entry point. Initialize the shell."""

    if not os.path.exists(filepath):
        click.confirm(
            "The given file does not exist. Do you wish to create it?",
            abort=True)

    try:
        click.echo('Please, confirm file unlock on the Trezor device.')
        store = TrezorEncryptedStore(filepath)
        shell = CofrShell(store=store)
        shell.cmdloop()
    except (NoTrezorFoundError, InvalidCofrFileError, PermissionError) as e:
        click.echo(e)
