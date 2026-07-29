from typing import Protocol


class PasswordHasher(Protocol):
    """Secondary port for password hashing and verification.

    Implemented by a driven adapter that wraps a hashing library (e.g. bcrypt
    or argon2). The core never hashes or verifies passwords directly; it
    depends on this port so the algorithm stays swappable and out of the
    domain.
    """

    def verify(self, password: str, password_hash: str) -> bool:
        """Check whether a plain-text password matches a stored hash.

        Args:
            password: The candidate plain-text password.
            password_hash: The stored hash to check against.

        Returns:
            ``True`` if the password matches the hash, ``False`` otherwise.
        """
        ...

    def hash(self, password: str) -> str:
        """Hash a plain-text password.

        Args:
            password: The plain-text password to hash.

        Returns:
            The resulting password hash, safe to store.
        """
        ...
