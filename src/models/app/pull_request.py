
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class PullRequest:
    """Model representing a pull request."""

    id: str
    title: str
    status: str = "OPEN"
    author: str = None
    repository_name: str = None
    source_branch: str = None
    target_branch: str = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    lines_added: int = 0
    lines_deleted: int = 0
    total_changes: int = 0

    def update_diff_stats(self, diff_data: dict[str, Any]) -> None:
        """Update diff statistics from diff data.

        Args:
            diff_data: Dictionary containing diff summary data
        """
        if 'summary' in diff_data:
            summary = diff_data['summary']
            self.lines_added = summary.get('lines_added', 0)
            self.lines_deleted = summary.get('lines_deleted', 0)
            self.total_changes = summary.get('total_changes', 0)
        else:
            files = diff_data.get('files', [])
            self.lines_added = sum(file.get('lines_added', 0) for file in files)
            self.lines_deleted = sum(file.get('lines_deleted', 0) for file in files)
            self.total_changes = self.lines_added + self.lines_deleted

@dataclass
class PullRequestFilter:
    status: str = "OPEN"
    limit: int = 10
    author: str = None

    def __post_init__(self):
        """OCI lifecycle details field uses upper case when filtering"""
        self.status = self.status.upper()

    field_mapping = {
        "status": "lifecycle_details",
        "limit": "limit",
        "author": "created_by"
    }

    def to_oci(self) -> dict[str, str]:
        result = asdict(self)
        return {self.field_mapping[k]: v for k, v in result.items() if v is not None}
