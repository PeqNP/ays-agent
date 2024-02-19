from typing import List
from typing_extensions import Optional

def get_name() -> str:
    return "ays-agent"

def get_version() -> str:
    return "1.0.0"

def save_config(
    org_secret: str,
    server: str,
    interval: Optional[int],
    parent: str,
    monitor_name: str,
    child: Optional[str],
    create_child: Optional[bool],
    node_type: Optional[str],
    managed: Optional[bool],
    heartbeat_timeout: Optional[int],
    heartbeat_level: Optional[str],
    value: Optional[float],
    value_name: Optional[str],
    value_threshold: Optional[str],
    values: Optional[List[float]],
    value_names: Optional[List[str]],
    value_thresholds: Optional[List[str]],
    status_message: Optional[str],
    status_state: Optional[str],
    monitor_resources: Optional[List[str]],
    monitor_file: Optional[str],
    monitor_program: Optional[str]
) -> None:
    pass
