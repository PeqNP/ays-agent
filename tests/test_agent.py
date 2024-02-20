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

@patch("ays_agent.cli.send_request")
@patch("ays_agent.cli.get_hostname", patch_string)
def test_send_value(p_send_request):
    # describe: send value; send all value options
    result = runner.invoke(cli.app, ["--org-secret=aaa", "--parent=com.unittest.send", "--value=5", "--value-name=disk", "--value-threshold='>10'"])
    assert result.exit_code == 0
    args, _ = p_send_request.call_args
    assert args[0] == cli.get_default_server()
    assert args[1] == {
        "org_secret": "aaa",
        "parent": {"property": "path", "value": "com.unittest.send"},
        "relationship": {"type": "parent", "monitor_name": "testing"},
        "value": {"value": 5, "name": "disk", "threshold": {"above": 10, "level": "critical"}}
    }, "it: should send provided values"

    # describe: send value; no values provided
    # it: should return default values
