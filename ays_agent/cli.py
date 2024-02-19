import typer

from enum import Enum
from rich import print
from typing import Optional
from typing_extensions import Annotated
from pathlib import Path

from ays_agent import get_name, get_version

class NodeType(str, Enum):
    machine = "machine"
    service = "service"
    vendor = "vendor"

class HeartbeatLevel(str, Enum):
    warning = "warning"
    error = "error"
    critical = "critical"

class StatusState(str, Enum):
    healthy = "healthy"
    warning = "warning"
    error = "error"
    critical = "critical"

class MonitorResource(str, Enum):
    all = "all"
    cpu = "cpu"
    hdd = "hdd"
    ram = "ram"
    net = "net"

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)

def _get_default_server():
    return "https://api.bithead.io:9443/agent/"

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{get_name()} v{get_version()}")
        raise typer.Exit()

@app.callback()
def main(
    version: Annotated[bool, typer.Option(
        help="Show the application's version and exit.",
        callback=_version_callback,
        show_default=False
    )] = False,
    server: Annotated[str, typer.Option(
        help="Path to the @ys server agent endpoint."
    )] = _get_default_server(),
    org_secret: Annotated[str, typer.Option(
        help="Organization secret. Required to interact with the respective org system graph."
    )] = "",
    interval: Annotated[int, typer.Option(
        help="Interval, in seconds, that the agent will report a value or status. This will make the agent act as a long-running service."
    )] = 300,
    parent: Annotated[str, typer.Option(
        help="The parent node path this agent will relate to.",
        show_default=False
    )] = None,
    monitor_name: Annotated[str, typer.Option(
        help="The name of the monitor that will be associated to the respective node. The default value will be the host name of the machine.",
        show_default=False
    )] = None,
    child: Annotated[str, typer.Option(
        help="A relative path to a child node that lives under the parent's node path.",
        show_default=False
    )] = None,
    create_child: Annotated[bool, typer.Option(
        help="Create a child node that lives under the parent's node path. The name of this child node will use the same name as the monitor."
    )] = False,
    node_type: Annotated[NodeType, typer.Option(
        help="The type of node to create when a child is created. Ignored when no child node is created."
    )] = NodeType.machine,
    managed: Annotated[bool, typer.Option(
        help="Agent is responsible for managing its own configuration."
    )] = True,

    heartbeat_timeout: Annotated[int, typer.Option(
        help="The timeout, in seconds, in which the agent will be considered unhealthy if it doesn't report within specified time.",
        show_default=False
    )] = None,
    heartbeat_level: Annotated[HeartbeatLevel, typer.Option(
        help="The alerting level to transition into if hearbeat timeout exceeded.",
        show_default=False
    )] = HeartbeatLevel.critical,

    value: Annotated[float, typer.Option(
        help="Report a single value to report to @ys.",
        show_default=False
    )] = None,
    value_name: Annotated[str, typer.Option(
        help="The respective name for the value.",
        show_default=False
    )] = None,
    value_threshold: Annotated[str, typer.Option(
        help="Thresholds are used to determine if the value is nominal or unhealthy. Options are `<N`, `>N`, `eN`, `neN`, and `N-N` where `N` is the threshold value. e.g. `<30` will trigger a threshold breach if `value` is greater than `30`.",
        show_default=False
    )] = None,

    values: Annotated[float, typer.Option(
        help="Report multiple values to @ys.",
        show_default=False
    )] = None,
    value_names: Annotated[str, typer.Option(
        help="The respective names for each value.",
        show_default=False
    )] = None,
    value_thresholds: Annotated[str, typer.Option(
        help="The threshold used to determine if the respective value is nominal or unhealthy.",
        show_default=False
    )] = None,

    status_message: Annotated[str, typer.Option(
        help="The message as to why the status is changing. Default is an empty string if `status-state` is provided.",
        show_default=False
    )] = None,
    status_state: Annotated[StatusState, typer.Option(
        help="The alerting level to transition into if hearbeat timeout exceeded. Default is `critical`, if only `status-message` is provided.",
        show_default=False
    )] = None,

    # Services
    monitor_resources: Annotated[MonitorResource, typer.Option(
        help="Monitor system resources.",
        show_default=False
    )] = None,

    monitor_file: Annotated[Optional[Path], typer.Option(
        help="Monitor the contents of a CSV file.",
        show_default=False
    )] = None,

    monitor_program: Annotated[Optional[Path], typer.Option(
        help="Execute a CLI program to derive value(s) to report on.",
        show_default=False
    )] = None,

    write_config: Annotated[bool, typer.Option(
        help="Write all options to configuration file."
    )] = False,
) -> None:
    print("Org secret:", org_secret)
    print("[bold red]Server:[/bold red]", f"[green]{server}[/green]")
    print("Interval:", interval)
    print("Parent:", parent)
    print("Monitor name:", monitor_name)
    print("Child:", child)
    print("Create child:", create_child)
    print("Node type:", node_type)
    print("Managed:", managed)

    print("Heartbeat timeout:", heartbeat_timeout)
    print("Heartbeat level:", heartbeat_level)

    print("Value:", value)
    print("Value name:", value_name)
    print("Value threshold:", value_threshold)

    print("Values:", values)
    print("Value names:", value_names)
    print("Value thresholds:", value_thresholds)

    print("Status message:", status_message)
    print("Status state:", status_state)

    print("Monitor resources:", monitor_resources)
    print("Monitor file:", monitor_file)
    print("Monitor program:", monitor_program)

    print("Write config:", write_config)
