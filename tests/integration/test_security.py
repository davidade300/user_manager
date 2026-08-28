from datetime import UTC, datetime, timedelta

import jwt
import pytest
import time_machine

from user_manager.adapters.secondary.security.password_hasher import (
    Argon2PasswordHasher,
)
from user_manager.adapters.secondary.security.token_issuer import (
    JwtTokenIssuer,
)
from user_manager.config import Settings
from user_manager.core.domain.exceptions import InvalidCredentials


class TestArgon2PasswordHasher:
    def test_hash_produces_a_verifiable_hash(self) -> None:
        hasher = Argon2PasswordHasher()

        password_hash = hasher.hash('correct_password')

        assert hasher.verify('correct_password', password_hash)

    def test_verify_with_wrong_password_returns_false(self) -> None:
        hasher = Argon2PasswordHasher()

        password_hash = hasher.hash('correct_password')

        assert hasher.verify('wrong_password', password_hash) is False

    def test_hash_does_not_store_password_in_plain_text(self) -> None:
        hasher = Argon2PasswordHasher()

        assert 'correct_password' not in hasher.hash('correct_password')


class TestJwtTokenIssuer:
    def test_issue_returns_a_token_decodable_with_the_secret(
        self, regular_user
    ) -> None:
        issuer = JwtTokenIssuer()

        token = issuer.issue(regular_user)
        claims = jwt.decode(
            token,
            Settings.JWT_SECRET_KEY,
            algorithms=[Settings.JWT_ALGORITHM],
        )

        assert claims['sub'] == str(regular_user.id)
        assert set(claims['roles']) == {
            role.value for role in regular_user.roles
        }

    def test_issue_fails_to_decode_with_the_wrong_secret(
        self, regular_user
    ) -> None:
        issuer = JwtTokenIssuer()

        token = issuer.issue(regular_user)

        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(
                token, 'wrong_secret', algorithms=[Settings.JWT_ALGORITHM]
            )

    def test_verify_returns_the_id_of_the_token_subject(
        self, regular_user
    ) -> None:
        issuer = JwtTokenIssuer()

        token = issuer.issue(regular_user)

        assert issuer.verify(token) == regular_user.id

    def test_verify_with_a_tampered_token_raises(self, regular_user) -> None:
        issuer = JwtTokenIssuer()
        token = issuer.issue(regular_user)

        with pytest.raises(InvalidCredentials):
            issuer.verify(f'{token}tampered')

    def test_verify_with_an_expired_token_raises(self, regular_user) -> None:
        issuer = JwtTokenIssuer()
        now = datetime(2026, 7, 25, tzinfo=UTC)

        with time_machine.travel(now, tick=False):
            token = issuer.issue(regular_user)

        past_expiration = now + timedelta(
            minutes=Settings.JWT_EXPIRATION_MINUTES + 1
        )
        with (
            time_machine.travel(past_expiration, tick=False),
            pytest.raises(InvalidCredentials),
        ):
            issuer.verify(token)

    def test_verify_with_a_malformed_token_raises(self) -> None:
        issuer = JwtTokenIssuer()

        with pytest.raises(InvalidCredentials):
            issuer.verify('not_a_token')
