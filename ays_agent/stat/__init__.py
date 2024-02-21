import sys

from typing import Union

# For some reason macOS uses 1000 as the base for byte conversions for network and disk activity.
# Please compare values produced here to that of Activity Monitor.
MACOS_BASE = 1000
OTHER_BASE = 1024

def get_base() -> int:
    """ Returns respective used for computation of byte-sizes given the
    respective platform the agent is running on."""
    if sys.platform == 'darwin':
        return MACOS_BASE
    else:
        return OTHER_BASE

def format_bytes(bytes: int, base: Union[int, None] = None) -> str:
    """ Pretty-print size of bytes. """
    base = base or 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < base:
            return f"{bytes:.2f}{unit}B"
        bytes /= base

