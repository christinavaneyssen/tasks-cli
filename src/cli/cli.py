import configparser
import logging
import sys
from pathlib import Path

import click

from src.cli.commands.pull_request_commands import pull_requests
from src.cli.errors import ErrorHandlingGroup, configure_error_handling

logging.getLogger("oci").setLevel(logging.CRITICAL)
log = logging.getLogger(__name__)

def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

def setup_logging(debug: bool) -> None:
    handler = logging.StreamHandler(sys.stdout) if debug else logging.FileHandler(Path("app.log"))
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[handler]
    )

@click.group(cls=ErrorHandlingGroup, context_settings={"allow_interspersed_args": True})
@click.option("--debug", is_flag=True)
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    setup_logging(debug)
    ctx.ensure_object(dict)

    # Store debug setting in context for access by other commands
    ctx.obj['debug'] = debug

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        click.echo("Debug mode enabled")
    else:
        # Suppress the default traceback display from Click
        sys.tracebacklimit = 0

    configure_error_handling(debug)


cli.add_command(pull_requests)
