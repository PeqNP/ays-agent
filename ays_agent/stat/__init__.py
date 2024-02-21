from typing import Union

def format_bytes(bytes: int, base: Union[int, None] = None) -> str:
    """ Pretty-print size of bytes. """
    base = base or 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < base:
            return f"{bytes:.2f}{unit}B"
        bytes /= base

