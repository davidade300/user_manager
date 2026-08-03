from typing import Protocol

from user_manager.core.domain.user import User


class TokenIssuer(Protocol):
    """Secondary port for issuing access tokens (e.g. JWT).

    Implemented by a driven adapter that wraps a token library. The core never
    signs tokens directly; it depends on this port so the token format and
    algorithm stay swappable and out of the domain.

    Verification of an incoming token (used by the JWT delivery adapter to
    validate a request and reconstruct the actor) will be added here when that
    adapter is built.
    """

    def issue(self, user: User) -> str:
        """Issue an access token for the given user.

        Args:
            user: The authenticated user; its id and roles are embedded as the
                token's claims.

        Returns:
            The signed access token, ready to be handed to the client.
        """
        ...
