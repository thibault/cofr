import os
import click

from .keyval import EncryptedStore


@click.group()
@click.option('-f', '--filepath', required=True, type=click.Path())
@click.pass_context
def cli(ctx, filepath):
    """Store and retrieve sensitive data using Trezor encryption.

    This software comes with NO WARRANTY whatsoever. Use it at your own risk.

    Also, this is NOT an official Trezor software.
    """

    if not os.path.exists(filepath):
        click.confirm(
            "The given file does not exist. Do you wish to create it?",
            abort=True)

    store = EncryptedStore(filepath)
    ctx.obj = store


@cli.resultcallback()
@click.pass_obj
def callback(obj, res, filepath):
    obj.close()


@cli.command()
@click.pass_obj
def list(obj):
    u"""List existing keys."""

    keys = obj.keys()
    click.echo('\n'.join(keys))


@cli.command()
@click.argument('key')
@click.argument('value')
@click.pass_obj
def set(obj, key, value):
    u"""Set the key value."""

    if key in obj:
        raise click.UsageError(
            'An existing key cannot be overriden. Remove it first.')

    obj[key] = value


@cli.command()
@click.argument('key')
@click.pass_obj
def get(obj, key):
    u"""Get the key value."""

    value = obj[key]
    click.echo_via_pager(value)


@cli.command()
@click.argument('key')
@click.confirmation_option(
    prompt='Are you sure you want to drop that key? It will be lost forever.')
@click.pass_obj
def rm(obj, key):
    u"""Delete an existing key.

    If the key is not present in the store, we just do nothing.
    """

    if key in obj:
        del obj[key]
