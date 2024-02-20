from .context import ays_agent

from typer.testing import CliRunner
from unittest.mock import patch

from ays_agent import get_name, get_version, cli

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

    # describe: threshold is above
    # describe: threshold is equal
    # describe: threshold is not equal
    # describe: threshold is range

    # describe: provide invalid threshold level
