from dataclasses import dataclass

from user_manager.core.domain.user import User


@dataclass(frozen=True)
class AuthResult:
    """Outcome of a successful authentication.

    Value object bundling the authenticated user with the access token issued
    for them, so a caller gets both the credential to carry on later requests
    and the user's data without a second round-trip.

    Attributes:
        user: The authenticated ``User`` entity.
        access_token: The signed access token issued for the user.
    """

    user: User
    access_token: str
