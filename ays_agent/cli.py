import typer

from typing import Optional

from ays_agent import get_name, get_version

app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{get_name()} v{get_version()}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    return
