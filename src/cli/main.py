import click
import logging

from commands.pull_request_commands import pull_request_commands

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()]
)
logging.getLogger("oci").setLevel(logging.CRITICAL)
log = logging.getLogger(__name__)


@click.group()
def cli():
    pass


cli.add_command(pull_request_commands)
