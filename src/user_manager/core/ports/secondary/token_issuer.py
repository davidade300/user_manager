from typing import Protocol
from uuid import UUID

from user_manager.core.domain.user import User


class TokenIssuer(Protocol):
    """Secondary port for issuing and verifying access tokens (e.g. JWT).

    Implemented by a driven adapter that wraps a token library. The core never
    signs or verifies tokens directly; it depends on this port so the token
    format and algorithm stay swappable and out of the domain.
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

    def verify(self, token: str) -> UUID:
        """Verify a token's signature and expiration.

        Used by the delivery adapter to validate an incoming request before
        reconstructing the actor (e.g. via the ``UserRepository``).

        Args:
            token: The access token to verify.

        Returns:
            The id of the user the token was issued for.

        Raises:
            InvalidCredentials: If the token is invalid, tampered with, or
                expired.
        """
        ...
