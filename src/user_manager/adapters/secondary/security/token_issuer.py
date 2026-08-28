"""Token issuing adapter.

Part of the secondary (driven) security adapter. Wraps ``PyJWT`` behind the
``TokenIssuer`` port, so the core never depends on the library directly.
"""

from datetime import UTC, datetime, timedelta

import jwt

from user_manager.config import Settings
from user_manager.core.domain.user import User
from user_manager.core.ports.secondary.token_issuer import TokenIssuer


class JwtTokenIssuer(TokenIssuer):
    """``TokenIssuer`` adapter issuing signed JWTs (via ``PyJWT``).

    Embeds the user's id (``sub``) and roles as claims, signed with
    ``Settings.JWT_SECRET_KEY`` and expiring after
    ``Settings.JWT_EXPIRATION_MINUTES``.
    """

    def issue(self, user: User) -> str:
        now: datetime = datetime.now(tz=UTC)
        payload: dict[str, datetime | list[str] | str] = {
            'sub': str(user.id),
            'roles': [role.value for role in user.roles],
            'iat': now,
            'exp': now + timedelta(minutes=Settings.JWT_EXPIRATION_MINUTES),
        }
        return jwt.encode(
            payload,
            Settings.JWT_SECRET_KEY,
            algorithm=Settings.JWT_ALGORITHM,
        )
