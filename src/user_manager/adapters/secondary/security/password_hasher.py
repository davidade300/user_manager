"""Password hashing adapter.

Part of the secondary (driven) security adapter. Wraps ``argon2-cffi``
behind the ``PasswordHasher`` port, so the core never depends on the
library directly.
"""

import argon2._password_hasher
from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

from user_manager.core.ports.secondary.password_hasher import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    """``PasswordHasher`` adapter backed by Argon2 (via ``argon2-cffi``)."""

    def __init__(self) -> None:
        self._hasher: argon2._password_hasher.PasswordHasher = Argon2Hasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except VerifyMismatchError:
            return False
