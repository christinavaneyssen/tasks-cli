import oci
import os.path
from oci.auth.security_token_container import SecurityTokenContainer
from oci.auth.signers import SecurityTokenSigner
from functools import lru_cache


class OCIClientFactory:
    def __init__(self, profile_name=None, config=None):
        """Initialize the factory with either a profile name or config object."""
        self.profile_name = profile_name or os.environ.get('OCI_CLI_PROFILE', 'DEFAULT')
        self.config = config or oci.config.from_file(profile_name=self.profile_name)
        self._signer = None

    @property
    def signer(self):
        """Lazily create and cache the signer."""
        if self._signer is None:
            self._signer = self._get_session_signer()
        return self._signer

    def _get_session_signer(self):
        """Create a session signer from the config."""
        token_path = self.config.get("security_token_file")
        if not token_path:
            raise RuntimeError("Couldn't find security token file")

        expanded_token_path = os.path.expanduser(token_path)

        with open(expanded_token_path, "r") as fh:
            token = fh.read()
            private_key = oci.signer.load_private_key_from_file(
                self.config.get("key_file"), self.config.get("pass_phrase")
            )

        token_container = SecurityTokenContainer(None, token)

        if not token_container.valid():
            raise RuntimeError("Refresh your OCI CLI session")

        return SecurityTokenSigner(token, private_key)

    def get_client(self, client_class):
        """Create a client instance of the specified class."""
        return client_class(self.config, signer=self.signer)


@lru_cache(maxsize=1)
def get_client_factory(profile_name=None):
    """Get or create a singleton client factory."""
    return OCIClientFactory(profile_name=profile_name)

def get_devops_client(profile_name=None):
    """Get a DevOpsClient instance."""
    factory = get_client_factory(profile_name)
    return factory.get_client(oci.devops.DevopsClient)