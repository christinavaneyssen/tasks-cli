import click
import json
from src.services.devops_service import DevOpsService
from src.infrastructure.oci_error_handling import OCIServiceError

pass_devops_service = click.make_pass_decorator(DevOpsService, ensure=True)

@click.group()
def pull_request_commands():
    pass

@pull_request_commands.command()
@click.option("--pull-request-id")
@pass_devops_service
def approve(devops_service, pull_request_id):
    try:
        devops_service.pull_request_approve(pull_request_id)
        click.echo(f"Pull request {pull_request_id} approved")
    except OCIServiceError as e:
        click.echo(f"Unexpected error: {e}")

@pull_request_commands.command()
@click.option("--pull-request-id")
@pass_devops_service
def merge(devops_service, pull_request_id):
    try:
        devops_service.merge(pull_request_id)
        click.echo(f"Pull request {pull_request_id} merged")
    except OCIServiceError as e:
        click.echo(f"Unexpected error: {e}")


@pull_request_commands.command()
@click.argument("json_file", type=click.File("r"))
@pass_devops_service
def create(devops_service, json_file):
    try:
        contents = json.load(json_file)
        devops_service.create_pull_request(contents)
        click.echo(f"Pull request created ")
    except OCIServiceError as e:
        click.echo(f"Unexpected error: {e}")
