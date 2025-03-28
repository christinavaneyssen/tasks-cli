"""Pull request service for working with repository pull requests.

This service provides business logic for pull request operations,
converting between OCI data models and application domain models.
"""

import logging
from typing import Any

from clients.oci.devops import DevOpsClient
from models.app.pull_request import PullRequestFilter
from src.core.config import config
from src.models.app.pull_request import PullRequest

logger = logging.getLogger(__name__)


class PullRequestService:
    """Service for working with pull requests.

    This service handles business operations related to pull requests, including:
    - Converting between OCI data and application domain models
    - Fetching pull requests with or without diff statistics
    - Managing pull request operations
    """

    def __init__(self) -> None:
        """Initialize the pull request service."""
        self.devops_client = DevOpsClient()
        self.repo_mapping = get_repo_ocid_mapping()

    def get_pull_requests(self, repo: str, filters: PullRequestFilter) -> list[PullRequest]:
        """Get pull requests for a repository.

        Args:
            repo: Repository name
            filters: What to filter by

        Returns:
            List of PullRequest domain objects
        """
        try:
            repo_id = self.repo_mapping[repo]
        except KeyError as e:
            raise ValueError(f"Repository '{repo}' not found in configuration. ") from e

        data = self.devops_client.get_pull_requests(repo_id, **filters.to_oci())

        return [PullRequest(**pr_data) for pr_data in data]

    def get_pull_request(self, repository_id: str, pull_request_id: str) -> PullRequest:
        """Get a specific pull request.

        Args:
            repository_id: The OCID of the repository
            pull_request_id: The ID of the pull request

        Returns:
            PullRequest domain object
        """
        data = self.devops_client.get_pull_request(repository_id, pull_request_id)
        return PullRequest(**data)

    def get_pull_request_diff(self, repository_id: str, pull_request_id: str) -> dict[str, Any]:
        """Get diff data for a pull request.

        Args:
            repository_id: The OCID of the repository
            pull_request_id: The ID of the pull request

        Returns:
            Dictionary with diff data including summary statistics
        """
        diff_data = self.devops_client.get_commit_diff(repository_id, pull_request_id)

        if diff_data and 'summary' not in diff_data:
            files = diff_data.get('files', [])
            lines_added = sum(file.get('lines_added', 0) for file in files)
            lines_deleted = sum(file.get('lines_deleted', 0) for file in files)

            diff_data['summary'] = {
                'lines_added': lines_added,
                'lines_deleted': lines_deleted,
                'total_changes': lines_added + lines_deleted
            }
        return diff_data

    def list_pull_requests(self, repos: list[str], **kwargs) -> list[PullRequest]:
        filters = PullRequestFilter(**kwargs)
        all_pull_requests = []

        for repo in repos:
            try:
                repo_pull_requests = self.get_pull_requests(repo, filters)
                all_pull_requests.extend(repo_pull_requests)
            except ValueError:
                logger.info(f"Repository {repo} not found in config.ini")

        for pull_request in all_pull_requests:
            diff_data = self.get_pull_request_diff(pull_request.repository_name, pull_request.id)
            pull_request.update_diff_stats(diff_data)

        return all_pull_requests

def get_repo_ocid_mapping() -> dict[str, str]:
    """Returns a dictionary mapping repository names to their OCIDs."""
    return dict(config.get_section("repos").items())
