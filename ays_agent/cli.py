#
# CLI for the agent-sensor
#
# Docs:
# - [Typer](https://typer.tiangolo.com/) - CLI API
# - [Rich](https://rich.readthedocs.io/en/stable/) - Display rich text to terminal
#

import logging
import typer
import requests
import socket
import time
import uvicorn

from enum import Enum
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi_utils.tasks import repeat_every
from rich import print
from typing import Optional
from typing_extensions import Annotated
from pathlib import Path

import ays_agent as lib

from ays_agent.stat.cpu import CPUMonitor
from ays_agent.stat.disk import DiskMonitor
from ays_agent.stat.memory import MemoryMonitor
from ays_agent.stat.network import NetworkMonitor

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

RESOURCE_MONITORS = {
    MonitorResource.cpu: CPUMonitor,
    MonitorResource.hdd: DiskMonitor,
    MonitorResource.ram: MemoryMonitor,
    MonitorResource.net: NetworkMonitor
}

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)

def get_default_server():
    return "https://api.bithead.io:9443/agent/"

def get_hostname():
    return socket.gethostname()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{lib.get_name()} v{lib.get_version()}")
        raise typer.Exit()

def send_request(server, json):
    resp = requests.request("POST", server, json=json)
    if resp.status_code != 204:
        print("Failed to make request to @ys server")
        print(resp)
        raise typer.Exit(1)
    else:
        raise typer.Exit()

# FastAPI Service

fastapp = FastAPI()

@fastapp.get("/test/")
async def test():
    return Response(status_code=204)

# Typer app

@app.callback()
def main(
    version: Annotated[bool, typer.Option(
        help="Show the application's version and exit.",
        callback=_version_callback,
        show_default=False
    )] = False,
    server: Annotated[str, typer.Option(
        help=f"Path to the @ys server agent endpoint. Default: {get_default_server()}"
    )] = None,
    org_secret: Annotated[str, typer.Option(
        help="Organization secret. Required to interact with the respective org system graph."
    )] = "",
    interval: Annotated[int, typer.Option(
        help="Interval, in seconds, that the agent will report a value or status. This will make the agent act as a long-running service. If a monitor is used, and the interval is not provided, the default interval will be 5 minutes."
    )] = None,
    port: Annotated[int, typer.Option(
        help="The port the agent listens to when becoming a long running service."
    )] = 9555,
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
        help="The type of node to create when a child is created. Ignored when no child node is created.",
        show_default=False
    )] = None,
    managed: Annotated[bool, typer.Option(
        help="Agent is responsible for managing its own configuration.",
        show_default=False
    )] = None,

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
    monitor_resources: Annotated[str, typer.Option(
        help="Monitor system resources. Available options: {list(MonitorResource.__members__}",
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
    dry_run: Annotated[bool, typer.Option(
        help="Emit the action that will take place, with the specified parameters, w/o sending data to @ys."
    )] = False,
) -> None:
    # Do not load options if writing new config. This prevents old options from
    # being merged with the new.
    if write_config:
        options = lib.get_empty_options()
    else:
        # Load options from disk, if any
        options = lib.load_options()
    # Merge options provided
    options.merge(
        org_secret=org_secret,
        server=server,
        interval=interval,
        parent=parent,
        monitor_name=monitor_name,
        child=child,
        create_child=create_child,
        node_type=node_type,
        managed=managed,
        heartbeat_timeout=heartbeat_timeout,
        heartbeat_level=heartbeat_level,
        value=value,
        value_name=value_name,
        value_threshold=value_threshold,
        values=values,
        value_names=value_names,
        value_thresholds=value_thresholds,
        status_message=status_message,
        status_state=status_state,
        monitor_resources=monitor_resources,
        monitor_file=monitor_file,
        monitor_program=monitor_program
    )

    if not options.server:
        options.server = get_default_server()
    if not options.monitor_name:
        options.monitor_name = get_hostname()

    # Ensure options are valid. This must happen regardless if CLI options are
    # provided or not as the user may write invalid config to the config file.
    server, msg = lib.get_agent_payload(options)

    # NOTE: Options must be checked before they are written to config.
    if write_config:
        lib.save_options(options)
        print("[green]Saved configuration to disk successfully.[/green]")
        raise typer.Exit()

    if (monitor_resources or monitor_program or monitor_file) and not options.interval:
        # Default is 5 minutes
        options.interval = 60 * 5
    if options.interval is not None and options.interval < 15:
        raise lib.AgentException("Interval provided ({options.interval}) must be 15 seconds or greater")

    if dry_run:
        print(f"Server: [green]{server}[/green]")

    if monitor_resources:
        resources = lib.strip_v(monitor_resources)
        for res in resources:
            if res not in MonitorResource.__members__:
                raise lib.AgentException(f"Invalid monitor resource ({res}). Available options are ({', '.join(MonitorResource.__members__)}).")
        monitor_options = monitor_resources.split(",")
        # Get class defintions of monitors to use
        if MonitorResource.all in monitor_options:
            monitors = RESOURCE_MONITORS.values()
        else:
            monitors = list(map(lambda x: RESOURCE_MONITORS[x], monitor_options))
        # Instantiate and start monitors
        monitors = list(map(lambda x: x(), monitors))
        for m in monitors: m.start()

        def get_message():
            values = []
            for monitor in monitors:
                # NOTE: This doesn't provide thresholds for values. If thresholds
                # are required, use the `com.bithead.template.agent_resources`
                # template.
                values.extend(monitor.get_values(options.interval))
            msg["values"] = values
            return msg

        if dry_run:
            print(f"Monitor resources: ({monitor_resources}) every {options.interval}s")
            print(get_message())
            raise typer.Exit()

        @fastapp.on_event("startup")
        @repeat_every(seconds=options.interval)
        async def run_forever() -> None:
            m = get_message()
            send_request(server, m)

        uvicorn.run(fastapp, host="0.0.0.0", port=port)
    elif monitor_program:
        # TODO: Execute program

        if dry_run:
            print(f"Monitor program: ({monitor_program}) every {options.interval}s")
            print(msg)
            raise typer.Exit()
    elif monitor_file:
        # TODO: Monitor file

        if dry_run:
            print(f"Monitor file: ({monitor_file}) every {options.interval}s")
            print(msg)
            raise typer.Exit()
    elif options.interval:
        if dry_run:
            print(f"Sending message every {options.interval}s")
            print(msg)
            raise typer.Exit()

        @fastapp.on_event("startup")
        @repeat_every(seconds=options.interval)
        async def run_forever() -> None:
            send_request(server, msg)

        uvicorn.run(fastapp, host="0.0.0.0", port=port)
    else:
        if dry_run:
            print(f"One-shot")
            print(msg)
            raise typer.Exit()

        send_request(server, msg)
