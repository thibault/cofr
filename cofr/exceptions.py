class NoTrezorFoundError(Exception):
    """No plugged Trezor wallet was found."""

    pass


class InvalidCofrFileError(Exception):
    """The file is invalid and cannot be parsed."""

    pass
