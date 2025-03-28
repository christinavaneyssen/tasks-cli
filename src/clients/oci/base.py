"""OCI client base implementation with integrated error handling.

This module provides the foundation for all OCI service clients in the application.
It handles authentication, configuration, and standardized error handling.
"""

import logging
import os
from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeVar

import oci
from oci.auth.security_token_container import SecurityTokenContainer
from oci.auth.signers import SecurityTokenSigner
from oci.util import to_dict

from src.core.config import config

logger = logging.getLogger(__name__)

T = TypeVar('T')


class OCIBaseClient:
    """Base class for OCI service clients.

    This class provides:
    1. OCI client initialization with profile management
    2. Automatic configuration loading from config.ini
    3. Standardized error handling for OCI operations
    4. Session token management
    """

    def __init__(self, service_name: str, client_class: type[T], profile_name: str = None) -> None:
        """Initialize the base OCI client.

        Args:
            service_name: Name of service config section in config.ini (e.g., 'devops')
            client_class: The OCI client class to instantiate (e.g., oci.devops.DevopsClient)
            profile_name: Name of authenticated OCI CLI profile to use
        """
        self.service_name = service_name
        self.client_class = client_class

        # Get OCI profile configuration
        self.profile_name = profile_name or self._get_profile_name()
        self.oci_config = self._load_oci_config()

        # Get service-specific configuration
        self.endpoint = config.get(self.service_name, "endpoint")
        self.retry_strategy = config.get(self.service_name, "retry")

        # Initialize the client
        self.client = self._create_client()

    def _get_profile_name(self) -> str:
        """Get the OCI profile name from config or environment variable."""
        # Priority: explicitly set in config > environment variable > DEFAULT
        return (
                config.get('oci', 'profile_name', fallback=None) or
                os.environ.get('OCI_CLI_PROFILE', 'DEFAULT')
        )

    def _load_oci_config(self) -> dict[str, Any]:
        """Load the OCI configuration from file."""
        return oci.config.from_file(profile_name=self.profile_name)

    def _get_signer(self)-> SecurityTokenSigner | None:
        """Create a session signer from the config."""
        token_path = self.oci_config.get("security_token_file")
        if not token_path:
            # If no token file is specified, use the API key signer
            return None

        expanded_token_path = os.path.expanduser(token_path)

        try:
            with open(expanded_token_path) as fh:
                token = fh.read()
                private_key = oci.signer.load_private_key_from_file(
                    self.oci_config.get("key_file"), self.oci_config.get("pass_phrase")
                )

            token_container = SecurityTokenContainer(None, token)

            if not token_container.valid():
                raise RuntimeError("Refresh your OCI CLI session")

            return SecurityTokenSigner(token, private_key)
        except FileNotFoundError:
            raise

    def _create_client(self) -> T:
        """Create the OCI client instance."""
        kwargs = {}

        if not self.oci_config.get("user"):
            signer = self._get_signer()
            kwargs["signer"] = signer

        if self.endpoint:
            kwargs['service_endpoint'] = self.endpoint

        if self.retry_strategy:
            kwargs['retry_strategy'] = self.retry_strategy


        return self.client_class(self.oci_config, **kwargs)

    def call(self,
                       operation: str,
                       response_key: str = 'data',
                       transform_func: Callable = None,
                       **kwargs) -> list[dict[str, Any]] | dict[str, Any]:
        """Generic method to call OCI list operations and extract data.

        Args:
            operation: The OCI client operation to call (e.g., self._client.list_pull_requests)
            response_key: The attribute of the response object that contains
                the list items (default: 'data')
            transform_func: Optional function to transform each item (default: to_dict)
            **kwargs: Arguments to pass to the operation

        Returns:
            List of dictionaries containing the transformed data
        """
        response = getattr(self.client, operation)(**kwargs)

        if transform_func is None:
            transform_func = to_dict

        data = getattr(response, response_key, [])

        try:
            result = []
            for item in data.items:
                result.append(transform_func(item))
        except KeyError:
            result = transform_func(data)

        return result


@lru_cache(maxsize=32)
def get_oci_client(service_name: str, client_class: type[T]) -> OCIBaseClient:
    """Get a cached instance of an OCI client.

    Args:
        service_name: Name of service config section in config.ini (e.g., 'devops')
        client_class: The OCI client class to instantiate (e.g., oci.devops.DevopsClient)

    Returns:
        A cached instance of the requested OCI client
    """
    return OCIBaseClient(service_name, client_class)
