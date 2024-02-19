from .context import ays_agent

from typer.testing import CliRunner

from ays_agent import get_name, get_version, cli

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{get_name()} v{get_version()}\n" in result.stdout

