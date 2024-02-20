from .context import ays_agent

import pytest

from typer.testing import CliRunner
from unittest.mock import patch

from ays_agent import get_name, get_version, cli, AgentException

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{get_name()} v{get_version()}\n" in result.stdout

def patch_string():
    return "testing"

def run_command(command, call):
    result = runner.invoke(cli.app, command)
    args, _ = call.call_args
    return result.exit_code, args

def call_cli(options, call):
    cli.main(**options)
    args, _ = call.call_args
    return args

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_send_value(p_send_request):
    req_options = ["--org-secret=aaa", "--parent=com.unittest.send"]
    # describe: send value; send all value options
    code, args = run_command(req_options + ["--value=5", "--value-name=disk", "--value-threshold=\">10:warning\""], p_send_request)
    assert code == 0
    assert args[0] == cli.get_default_server()
    assert args[1] == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.send"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "value": {"value": 5.0, "name": "disk", "threshold": {"above": 10.0, "level": "warning"}}
    }, "it: should send provided values"

    # describe: send only value
    code, args = run_command(req_options + ["--value=5"], p_send_request)
    assert code == 0
    assert args[1] == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.send"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "value": {"value": 5.0, "name": "value"}
    }, "it: should send default values"

    # describe: threshold is below
    code, args = run_command(req_options + ["--value=3.2", "--value-threshold=<7.1:error"], p_send_request)
    assert code == 0
    assert args[1] == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.send"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "value": {"value": 3.2, "name": "value", "threshold": {"below": 7.1, "level": "error"}}
    }, "it: should send default values"

    # describe: threshold is equal
    code, args = run_command(req_options + ["--value=3.2", "--value-threshold=e2:critical"], p_send_request)
    assert code == 0
    assert args[1] == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.send"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "value": {"value": 3.2, "name": "value", "threshold": {"equal": 2, "level": "critical"}}
    }, "it: should send default values"

    # describe: threshold is not equal
    code, args = run_command(req_options + ["--value=3.2", "--value-threshold=ne2:critical"], p_send_request)
    assert code == 0
    assert args[1] == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.send"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "value": {"value": 3.2, "name": "value", "threshold": {"nequal": 2, "level": "critical"}}
    }, "it: should send correct values"

    # describe: threshold is range
    code, args = run_command(req_options + ["--value=3.2", "--value-threshold=40.2-50.5"], p_send_request)
    assert code == 0
    # it: should set default threshold value to `critical`
    assert args[1] == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.send"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "value": {"value": 3.2, "name": "value", "threshold": {"outside": {"min": 40.2, "max": 50.5}, "level": "critical"}}
    }, "it: should send correct values"

    args = {
        "org_secret": "aaa",
        "parent": "com.unittest.send",
        "value": "4.1",
        "value_threshold": "b34"
    }

    # describe: provide inavlid threshold type
    with pytest.raises(AgentException, match=r"^Invalid threshold type for value \(b34\)$"):
        cli.main(**args)

    # describe: provide invalid threshold level
    args["value_threshold"] = ">34:super"
    with pytest.raises(AgentException, match=r"^Invalid threshold level \(super\). Available options are \(warning, error, critical\)$"):
        cli.main(**args)

    # describe: invalid value
    args["value"] = "b34"
    args["value_threshold"] = ">34"
    with pytest.raises(ValueError):
        cli.main(**args)

    # describe: invalid min value
    args["value"] = "34"
    args["value_threshold"] = "o34-40"
    with pytest.raises(ValueError):
        cli.main(**args)

    # describe: invalid max value
    args["value"] = "34"
    args["value_threshold"] = "34-o40"
    with pytest.raises(ValueError):
        cli.main(**args)

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_send_values(p_send_request):
    options = {
        "org_secret": "aaa",
        "parent": "com.unittest.values",
        "values": "4.1,5.0,7.7",
        "value_names": "cpu, ram,hdd",
        "value_thresholds": "<1.3,>8.7:error,"
    }

    # describe: all value options provided; one threshold omitted; name has space
    req, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.values"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "values": [
            {"value": 4.1, "name": "cpu", "threshold": {"below": 1.3, "level": "critical"}},
            {"value": 5.0, "name": "ram", "threshold": {"above": 8.7, "level": "error"}},
            {"value": 7.7, "name": "hdd"}
        ]
    }, "it: should send correct values"

    # describe: invalid number of names
    options["value_names"] = "cpu,ram"
    with pytest.raises(AgentException, match=r"^The number of names \(2\) must match the number of values \(3\) provided$"):
        cli.main(**options)

    # describe: invalid number of thresholds
    options["value_names"] = "cpu,ram,hdd"
    options["value_thresholds"] = "<1.3,>8.7"
    with pytest.raises(AgentException, match=r"^The number of thresholds \(2\) must match the number of values \(3\) provided$"):
        cli.main(**options)

    # describe: value options provided; name missing
    options.pop("value_thresholds")
    options["value_names"] = "cpu,,hdd"
    req, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.values"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "values": [
            {"value": 4.1, "name": "cpu"},
            # it: should set default value to "value" + index
            {"value": 5.0, "name": "value1"},
            {"value": 7.7, "name": "hdd"}
        ]
    }, "it: should send correct values"

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_send_status(p_send_request):
    options = {
        "org_secret": "aaa",
        "parent": "com.unittest.values",
        "status_message": "This is only a test",
    }

    # describe: provide status; no state provided
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.values"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "status": {
            "message": "This is only a test",
            # it: should return correct default value
            "state": "critical"
        }
    }, "it: should send correct values"

    # describe: provide status state; no status message
    options.pop("status_message")
    options["status_state"] = "warning"
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.values"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "status": {
            # it: should return correct default value
            "message": "",
            "state": "warning"
        }
    }, "it: should send correct values"

    # describe: provide invalid state
    options["status_state"] = "super"
    with pytest.raises(AgentException, match=r"^Invalid status state \(super\). Available options are \(healthy, warning, error, critical\)$"):
        cli.main(**options)

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_create_child(p_send_request):
    options = {
        "org_secret": "aaa",
        "parent": "com.unittest.create_child",
        "child": "a-child"
    }

    # describe: provide status; no state provided
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.create_child"},
        "relationship": {"type": "child", "monitor_name": "testing", "path": "a-child"},
    }, "it: should send correct values"

    # describe: child name does not match naming convention
    options["child"] = "a child**node"
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.create_child"},
        "relationship": {"type": "child", "monitor_name": "testing", "path": "a-child-node"},
    }, "it: should send correct values"

    # describe: child name has invalid first character
    options["child"] = "0name"
    with pytest.raises(AgentException, match=r"^A node name must start with one of the following characters \(abcdefghijklmnopqrstuvwxyz\)$"):
        cli.main(**options)

    # describe: child name is greater than max length
    options["child"] = "e123456789012345678901234567890"
    assert len(options["child"]) == 31 # sanity
    with pytest.raises(AgentException, match=r"^A node name may not exceed 30 characters$"):
        cli.main(**options)

    # describe: creat child by adopting the monitor name
    options.pop("child")
    options["create_child"] = True
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.create_child"},
        "relationship": {"type": "child", "monitor_name": "testing", "path": "testing"},
    }, "it: should adopt the monitor name for the child node name"

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_agent_type(p_send_request):
    options = {
        "org_secret": "aaa",
        "parent": "com.unittest.agent_type",
        "create_child": True,
        "node_type": "machine"
    }

    # describe: provide a valid node type
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.agent_type"},
        "relationship": {"type": "child", "monitor_name": "testing", "path": "testing"},
        "type": "machine"
    }, "it: should adopt the monitor name for the child node name"

    # describe: provide invalid node type
    options["node_type"] = "incorrect"
    with pytest.raises(AgentException, match=r"^Invalid agent type \(incorrect\). Available options are \(machine, service, vendor\)$"):
        cli.main(**options)

    # describe: node type provided; not creating a child
    options["node_type"] = "machine"
    options.pop("create_child")
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.agent_type"},
        "relationship": {"type": "parent", "monitor_name": "testing"}
    }, "it: should ignore the node type"

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_managed_node(p_send_request):
    options = {
        "org_secret": "aaa",
        "parent": "com.unittest.agent_type",
        "create_child": True,
        "managed": True
    }

    # describe: provide managed
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.agent_type"},
        "relationship": {"type": "child", "monitor_name": "testing", "path": "testing"},
        "managed": True
    }, "it: should be a managed node"

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_heartbeat(p_send_request):
    options = {
        "org_secret": "aaa",
        "parent": "com.unittest.heartbeat",
        "heartbeat_timeout": 30
    }

    # describe: provide heartbeat config; no level provided
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.heartbeat"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "heartbeat": {
            "timeout": 30,
            # it: should set to default value
            "level": "critical"
        }
    }, "it: should return heartbeat config"

    # describe: provide heartbeat config; level provided
    options["heartbeat_level"] = "warning"
    _, args = call_cli(options, p_send_request)
    assert args == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.heartbeat"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "heartbeat": {
            "timeout": 30,
            "level": "warning"
        }
    }, "it: should set heartbeat level"

    # describe: provide invalid heartbeat timeout
    options["heartbeat_timeout"] = "o30"
    with pytest.raises(ValueError):
        cli.main(**options)

    # describe: provide invalid heartbeat level
    options["heartbeat_timeout"] = 30
    options["heartbeat_level"] = "incorrect"
    with pytest.raises(AgentException, match=r"^Invalid heartbeat level \(incorrect\). Available options are \(warning, error, critical\)$"):
        cli.main(**options)
