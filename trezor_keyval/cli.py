import click


@click.group()
def cli():
    """Script entry point."""
    pass


@cli.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    u"""Set the key value."""
    pass


@cli.command()
@click.argument('key')
def get(key):
    u"""Get the key value."""
    pass


@cli.command()
def list():
    u"""List existing keys."""
    click.echo("list")


@cli.command()
@click.argument('key')
def rm(key):
    u"""Delete an existing key."""
    pass
