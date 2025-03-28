"""OCI DevOps client implementation.

This module provides a client for interacting with the OCI DevOps service.
It handles repository and pull request operations.
"""

from typing import Any

import oci.devops

from src.clients.oci.base import OCIBaseClient


class DevOpsClient(OCIBaseClient):
    """Client for OCI DevOps API operations."""

    def __init__(self) -> None:
        """Initialize the DevOps client."""
        super().__init__(
            service_name="devops",
            client_class=oci.devops.DevopsClient
        )

    def get_pull_requests(self, repository_id: str, **kwargs) -> list[dict[str, Any]]:
        """Get pull requests for a repository.

        Args:
            repository_id: The OCID of the repository
        """
        return self.call(
            operation="list_pull_requests",
            repository_id=repository_id,
            **kwargs
        )

    def get_pull_request(self, repository_id: str, pull_request_id: str) -> dict[str, Any]:
        """Get a specific pull request by ID.

        Args:
            repository_id: The OCID of the repository
            pull_request_id: The ID of the pull request

        Returns:
            Pull request data dictionary
        """
        return self.call(
            operation="get_pull_request",
            repository_id=repository_id,
            pull_request_id=pull_request_id
        )

    def get_commit_diff(self, repository_id: str, pull_request_id: str) -> dict[str, Any]:
        """Get the diff for a pull request.

        Args:
            repository_id: The OCID of the repository
            pull_request_id: The ID of the pull request

        Returns:
            Dictionary with diff data and summary statistics
        """
        diff_data = self.call(
            operation="get_commit_diff",
            repository_id=repository_id,
            pull_request_id=pull_request_id
        )

        return diff_data
