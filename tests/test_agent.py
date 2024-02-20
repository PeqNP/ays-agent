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
    cli.main(**options)
    call_args, _ = p_send_request.call_args
    req, args = call_args
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
    cli.main(**options)
    call_args, _ = p_send_request.call_args
    req, args = call_args
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
