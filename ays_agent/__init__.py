import logging
import re

from typing import List
from typing_extensions import Optional, Self

def get_name() -> str:
    return "ays-agent"

def get_version() -> str:
    return "1.0.0"

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

    @staticmethod
    def load() -> Self:
        # TODO: Load from file or create instance CLIOptions with empty values
        return CLIOptions(
            org_secret="",
            server="",
            parent="",
            monitor_name=""
        )

    def setv(self, name, arg) -> None:
        """ Sets the value for Self property `name` from `arg` values. """
        val = arg.get(name, None)
        if val:
            self.__dict__[name] = val

    def merge(self, **kwargs) -> None:
        """ Merge existing options with options provided from CLI. """
        self.cli_options = CLIOptions(**kwargs)

        keys = list(self.__dict__.keys())
        try:
            keys.remove("cli_options")
        except:
            pass
        for key in keys:
            self.setv(key, kwargs)

    def save(self) -> None:
        if not self.cli_options:
            raise AgentException("No CLI options provided to save.")
        # TODO: Save provided CLI options to disk

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
        "relationship": {"type": "parent", "monitor_name": options.monitor_name},
    }
    if options.value:
        params["value"] = get_value(options.value_name, options.value, options.value_threshold)
    elif options.values:
        params["values"] = get_values(options.values, options.value_names, options.value_thresholds)
    return options.server, params


AVAIL_THRESH_LEVELS = ["warning", "error", "critical"]

def get_value(name: Union[str, None], value: str, threshold: Union[str, None]) -> dict:
    """ Returns a dict value that represents an `AgentValue`. """
    value = {
        "name": name or "value",
        "value": float(value),
        "threshold": get_threshold(threshold)
    }
    if not value.get("threshold"):
        value.pop("threshold", None)
    return value

def get_values(names: Union[str, None], values: str, thresholds: Union[str, None]) -> List[dict]:
    """ Returns an array of dict values that represent an `AgentValue`. """
    pass

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
