from oci.devops.models import ExecuteMergePullRequestDetails, ReviewPullRequestDetails, UpdateReviewerDetails, UpdatePullRequestDetails, CreatePullRequestDetails
from src.infrastructure.oci_client_factory import get_devops_client
from src.infrastructure.oci_error_handling import handle_oci_errors
USER_ID = ""


class DevOpsService:

    def __init__(self, client=None):
        self.client = client or get_devops_client()

    @handle_oci_errors
    def merge(self, pr_id):
        pull_request_details = self.client.get_pull_request(pr_id).data

        return self.client.merge_pull_request(
            pull_request_id=pr_id,
            merge_pull_request_details=ExecuteMergePullRequestDetails(
                action_type="EXECUTE",
                merge_strategy="FAST_FORWARD_ONLY",
                commit_message=f"Merge pull request from {pull_request_details.source_branch} to {pull_request_details.destination_branch}",
                post_merge_action="DELETE_SOURCE_BRANCH"
            )
        )

    @handle_oci_errors
    def approve(self, pr_id):
        self._update_reviewers(pr_id)
        return self.client.review_pull_request(
            pr_id,
            review_pull_request_details=ReviewPullRequestDetails(action="APPROVE")
        )

    @handle_oci_errors
    def is_reviewer(self, pr_id):
        pull_request = self.client.get_pull_request(pr_id).data
        if pull_request.reviewers:
            for reviewer in pull_request.reviewers:
                if reviewer.principal_id == USER_ID:
                    return True
        return False

    @handle_oci_errors
    def _update_reviewers(self, pr_id):
        pull_request = self.client.get_pull_request(pr_id)
        updated_reviewers = []
        for reviewer in pull_request.reviewers:
            updated_reviewers.append(UpdateReviewerDetails(principal_id=reviewer.principal_id))
        updated_reviewers.append(UpdateReviewerDetails(principal_id=USER_ID))
        return self.client.update_pull_request(
            pr_id,
            update_pull_request_details=UpdatePullRequestDetails(
                reviewers=updated_reviewers
            )
        )

    @handle_oci_errors
    def get_repo(self, repo_id):
        return self.client.get_repository(repo_id).data

    @handle_oci_errors
    def create_pull_request(self, content):
        if not content.get("destination_branch"):
            repo = self.get_repo()
            content["destination_branch"] = repo.default_branch

        return self.client.create_pull_request(
            create_pull_request_details=CreatePullRequestDetails(**content)
        )
