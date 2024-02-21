import logging
import os
import re

from typing import List, Union
from typing_extensions import Optional, Self

from yaml import load, dump, safe_load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper

AVAIL_THRESH_LEVELS = ["warning", "error", "critical"]
AVAIL_STATUS_STATES = ["healthy", "warning", "error", "critical"]
AVAIL_AGENT_TYPES = ["machine", "service", "vendor"]

NODE_RESERVED_NAMES = ["measurements", "c", "xff"]
NODE_VALID_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789_-"
NODE_VALID_FIRST_CHARS = "abcdefghijklmnopqrstuvwxyz"
NODE_MAX_NAME_LENGTH = 30

CONFIG_PATH = None

def get_name() -> str:
    return "ays-agent"

def get_version() -> str:
    return "1.0.0"

def set_config_path(path: str) -> None:
    """ Set the @ys configuration path.

    Use only for testing.
    """
    global CONFIG_PATH
    CONFIG_PATH = path

def get_config_path():
    global CONFIG_PATH
    if CONFIG_PATH:
        return CONFIG_PATH
    home_path = os.path.expanduser("~")
    path = os.path.join(home_path, ".ays-agent")
    return path

def write_yaml(fh, obj):
    dump(obj, fh)

def read_yaml(fh):
    return load(fh, Loader=Loader)

class AgentException(Exception):
    pass

class CLIOptions(object):
    def __init__(
        self,
        org_secret: str,
        server: str,
        parent: str,
        monitor_name: Optional[str] = None,
        interval: Optional[int] = None,
        child: Optional[str] = None,
        create_child: Optional[bool] = None,
        node_type: Optional[str] = None,
        managed: Optional[bool] = None,
        heartbeat_timeout: Optional[int] = None,
        heartbeat_level: Optional[str] = None,
        value: Optional[float] = None,
        value_name: Optional[str] = None,
        value_threshold: Optional[str] = None,
        values: Optional[List[float]] = None,
        value_names: Optional[List[str]] = None,
        value_thresholds: Optional[List[str]] = None,
        status_message: Optional[str] = None,
        status_state: Optional[str] = None,
        monitor_resources: Optional[List[str]] = None,
        monitor_file: Optional[str] = None,
        monitor_program: Optional[str] = None
    ):
        self.org_secret = org_secret
        self.server = server
        self.parent = parent
        self.monitor_name = monitor_name
        self.interval = interval
        self.child = child
        self.create_child = create_child
        self.node_type = node_type
        self.managed = managed
        self.heartbeat_timeout = heartbeat_timeout
        self.heartbeat_level = heartbeat_level
        self.value = value
        self.value_name = value_name
        self.value_threshold = value_threshold
        self.values = values
        self.value_names = value_names
        self.value_thresholds = value_thresholds
        self.status_message = status_message
        self.status_state = status_state
        self.monitor_resources = monitor_resources
        self.monitor_file = monitor_file
        self.monitor_program = monitor_program

        # Options provided to the app from the CLI
        self.cli_options = None

    def setv(self, name, arg) -> None:
        """ Sets the value for Self property `name` from `arg` values. """
        val = arg.get(name, None)
        if val:
            self.__dict__[name] = val

    def get_options(self) -> dict:
        """ Returns all options that can be saved. """
        opts = self.__dict__.copy()
        opts.pop("cli_options", None)
        return opts

    def merge(self, **kwargs) -> None:
        """ Merge existing options with options provided from CLI. """
        self.cli_options = CLIOptions(**kwargs)
        keys = list(self.get_options().keys())
        for key in keys:
            self.setv(key, kwargs)

# Public API

def load_options(path: str) -> CLIOptions:
    """ Load ays agent server options from config file.

    Returns an options, if config file not found.
    """
    if os.path.isfile(path):
        with open(path, "r") as fh:
            opts = read_yaml(fh)
        return CLIOptions(**opts)
    return CLIOptions(
        org_secret="",
        server="",
        parent="",
        monitor_name=""
    )

def save_options(options: CLIOptions) -> None:
    """ Save options to disk. """
    path = get_config_path()
    opts = options.get_options()
    keys = list(opts.keys())
    for key in keys:
        if opts[key] is None:
            del opts[key]
    with open(path, "w") as fh:
        write_yaml(fh, opts)

def get_agent_payload(options) -> None:
    """ Returns a request that represents an `AgentPayload`. """
    if not options.org_secret:
        raise AgentException("'org_secret' must be provided")
    if not options.parent:
        raise AgentException("'parent' must be provided")
    if not options.monitor_name:
        raise AgentException("'monitor_name' must be provided")
    params = {
        "org_secret": options.org_secret,
        "parent": {"property": "path", "value": options.parent},
    }
    if options.child:
        params["relationship"] = {"type": "child", "monitor_name": options.monitor_name, "path": get_formatted_node_name(options.child)}
    elif options.create_child:
        params["relationship"] = {"type": "child", "monitor_name": options.monitor_name, "path": options.monitor_name}
    else:
        params["relationship"] = {"type": "parent", "monitor_name": options.monitor_name}
    if options.managed is not None:
        params["managed"] = options.managed
    if options.heartbeat_timeout:
        params["heartbeat"] = {
            "timeout": int(options.heartbeat_timeout),
            "level": get_heartbeat_level(options.heartbeat_level)
        }
    if options.node_type and (options.child or options.create_child):
        params["type"] = get_agent_type(options.node_type.lower())
    if options.value:
        params["value"] = get_value(options.value_name, options.value, options.value_threshold)
    elif options.values:
        params["values"] = get_values(options.value_names, options.values, options.value_thresholds)
    elif options.status_message or options.status_state:
        params["status"] = get_status(options.status_message, options.status_state)
    return options.server, params

# Private API

def get_heartbeat_level(level: str) -> str:
    """ Returns heartbeat level. Returns default if not provided. """
    if level and level not in AVAIL_THRESH_LEVELS:
        raise AgentException(f"Invalid heartbeat level ({level}). Available options are ({', '.join(AVAIL_THRESH_LEVELS)})")
    elif not level:
        level = "critical"
    return level


def get_agent_type(agent_type: str) -> str:
    """ Returns agent type, if valid. """
    if agent_type not in AVAIL_AGENT_TYPES:
        raise AgentException(f"Invalid agent type ({agent_type}). Available options are ({', '.join(AVAIL_AGENT_TYPES)})")
    return agent_type

def get_formatted_node_name(name: str) -> str:
    """ Standardize a node name to follow @ys node name conventions.

    This removes all characters outside of the acceptable range with hyphens.
    Duplicate hyphens are removed.
    """
    if not name:
        raise AgentException("Name must be greater than zero")
    if name[0] not in NODE_VALID_FIRST_CHARS:
        raise AgentException(f"A node name must start with one of the following characters ({NODE_VALID_FIRST_CHARS})")
    if len(name) > NODE_MAX_NAME_LENGTH:
        raise AgentException(f"A node name may not exceed {NODE_MAX_NAME_LENGTH} characters")
    node_name = ""
    for c in name:
        if c not in NODE_VALID_CHARS:
            node_name += "-"
        else:
            node_name += c
    # Remove duplicate hyphens, if any
    node_name = re.sub(r"-+", "-", node_name)
    return node_name

def get_status_state(state) -> str:
    """ Returns provided status state or `critical` if not provided. """
    if state and state not in AVAIL_STATUS_STATES:
        raise AgentException(f"Invalid status state ({state}). Available options are ({', '.join(AVAIL_STATUS_STATES)})")
    elif not state:
        state = "critical"
    return state

def get_status(message, state) -> dict:
    """ Returns a dict that represents an `AgentStatus`. """
    return {
        "message": message or "",
        "state": get_status_state(state)
    }

def get_value(name: Union[str, None], value: str, threshold: Union[str, None], index: Optional[int] = None) -> dict:
    """ Returns a dict value that represents an `AgentValue`. """
    value = {
        "name": name or (index is None and "value" or f"value{index}"),
        "value": float(value),
        "threshold": get_threshold(threshold)
    }
    if not value.get("threshold"):
        value.pop("threshold", None)
    return value

def strip_v(v, values):
    if v:
        return list(map(lambda x: x.strip(), v.split(",")))
    else:
        return [None] * len(values)

def get_values(names: Union[str, None], values: str, thresholds: Union[str, None]) -> List[dict]:
    """ Returns an array of dict values that represent an `AgentValue`. """
    values = strip_v(values, values)
    names = strip_v(names, values)
    if len(names) != len(values):
        raise AgentException(f"The number of names ({len(names)}) must match the number of values ({len(values)}) provided")
    thresholds = strip_v(thresholds, values)
    if len(thresholds) != len(values):
        raise AgentException(f"The number of thresholds ({len(thresholds)}) must match the number of values ({len(values)}) provided")
    r_values = []
    for idx, v in enumerate(values):
        v = get_value(names[idx], v, thresholds[idx], idx)
        r_values.append(v)
    return r_values

def get_threshold_level(level_parts: List[str]) -> str:
    """ Returns a threshold value given threshold parts.

    The first part is ignored. The second part is the threshold value.
    """
    if len(level_parts) > 1:
        level = level_parts[1]
        if level not in AVAIL_THRESH_LEVELS:
            raise AgentException(f"Invalid threshold level ({level}). Available options are ({', '.join(AVAIL_THRESH_LEVELS)})")
    else:
        level = "critical"
    return level

def get_threshold(thresh: str) -> dict:
    """ Returns a dict that represents an `AgentThreshold`. """
    if not thresh:
        return None
    # Apparently the `click` / `typer` library do not remove quotes around values
    thresh = thresh.lower().strip("'").strip('"')

    # Outside threshold range
    if "-" in thresh:
        if ":" in thresh:
            parts = thresh.split(":")
        else:
            parts = [thresh]
        _min, _max = parts[0].split("-")
        level = get_threshold_level(parts)
        return {"outside": {"min": float(_min), "max": float(_max)}, "level": level}

    # Threshold type
    if thresh.startswith(">"):
        thresh_type = "above"
    elif thresh.startswith("<"):
        thresh_type = "below"
    elif thresh.startswith("e"):
        thresh_type = "equal"
    elif thresh.startswith("ne"):
        thresh_type = "nequal"
    else:
        raise AgentException(f"Invalid threshold type for value ({thresh})")

    # Threshold level
    level_parts = thresh.split(":")
    level = get_threshold_level(level_parts)

    # Threshold value
    numeric_part = re.search(r'\d+(\.\d+)?', thresh).group()

    # NOTE: `float` will raise `ValueError` if it's not valid
    return {thresh_type: float(numeric_part), "level": level}
