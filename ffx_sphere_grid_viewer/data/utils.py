import os
import sys
from functools import partial


def s16(integer: int) -> int:
    return ((integer & 0xffff) ^ 0x8000) - 0x8000


def add_bytes(*values: int) -> int:
    value = 0
    for position, byte in enumerate(values):
        value += byte * (256 ** position)
    return value


def get_resource_path(relative_path: str,
                      file_directory: str | None = None,
                      ) -> str:
    """Get the absolute path to a resource, necessary for PyInstaller."""
    try:
        file_directory: str = sys._MEIPASS
    except AttributeError:
        if file_directory is None:
            file_directory = os.path.dirname(__file__)
    resource_path = os.path.join(file_directory, relative_path)

    return resource_path


open_cp1252 = partial(open, encoding='cp1252')
open_cp1252.__doc__ = 'Open file with encoding \'cp1252\'.'
