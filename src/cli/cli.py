import configparser
import logging
import sys
from pathlib import Path

import click

from .commands.pull_request_commands import pull_requests

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


@click.group(context_settings={"allow_interspersed_args": True})
@click.option("--debug", flag=True)
def cli(debug: bool) -> None:
    setup_logging(debug)


cli.add_command(pull_requests)
