import sys

from typing import Union

# We (as in society) can't decide if the base is 1000 or 1024. HD manufacturer's
# prefer 1000, while IT prefers 1024. This uses the respective base depending
# on the platform's preference. Windows & Linux = 1024. macOS = 1000.
MACOS_BASE = 1000
OTHER_BASE = 1024

def get_platform():
    return sys.platform.lower()

def is_darwin():
    return get_platform() == "darwin"

def is_windows():
    return get_platform() == "windows"

def get_base() -> int:
    """ Returns respective used for computation of byte-sizes given the
    respective platform the agent is running on."""
    if is_darwin():
        return MACOS_BASE
    else:
        return OTHER_BASE

def get_default_mountpoint():
    if is_darwin():
        # TODO: This may be a different name on <=Catalina. I can't get a
        # definitive answer.
        return "/System/Volumes/Data"
    else:
        # TODO: Determine default root path for Linux & Windows
        # This may require returning `C:\` on Windows
        return "/"

def format_bytes(bytes: int, base: Union[int, None] = None) -> str:
    """ Pretty-print size of bytes. """
    base = base or OTHER_BASE
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < base:
            return f"{bytes:.2f}{unit}B"
        bytes /= base

def get_megabytes(bytes: int, base: Union[int, None] = None) -> int:
    """ Transforms bytes value to megabytes value. """
    base = base or OTHER_BASE
    return bytes / base / base
