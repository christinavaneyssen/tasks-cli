"""CLI commands for working with pull requests."""
from typing import Literal

import click
from tabulate import tabulate

from src.services.pull_requests.service import PullRequestService


@click.group()
def pull_requests() -> None:
    """Commands for working with pull requests."""
    pass


@pull_requests.command()
@click.argument("repos", nargs=-1)
@click.option("--status", type=click.Choice(["open"]), default="open")
@click.option("--limit", type=int, default=10)
def list(repos: tuple[str, ...], status: Literal["open"], limit: int) -> None:
    """List pull requests for a repository."""
    service = PullRequestService()
    kwargs = {"status": status, "limit": limit}
    pull_requests = service.list_pull_requests(
        repos, **kwargs)

    if pull_requests:
        headers = ["Title", "Status", "Created", "Changes"]
        data = [
            [
                pr.title,
                pr.status,
                pr.created_at.strftime("%Y-%m-%d %H:%M"),
                f"{pr.total_changes} (+{pr.lines_added}/-{pr.lines_deleted})"
            ]
            for pr in pull_requests
        ]
        click.echo(tabulate(data, headers=headers, tablefmt="pretty"))
    else:
        click.echo("No pull requests found.")
