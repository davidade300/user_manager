from uuid import UUID

from user_manager.core.domain.user import User
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.token_issuer import TokenIssuer
from user_manager.core.ports.secondary.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.memory: dict[UUID, User] = {}

    def get_by_id(self, user_id: UUID) -> User:
        # pyrefly: ignore [bad-return]
        return self.memory.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for user in self.memory.values():
            if user.email == email:
                return user
        return None

    def get_by_username(self, user_name: str) -> User | None:
        for user in self.memory.values():
            if user.user_name == user_name:
                return user
        return None

    def save(self, user: User) -> None:
        self.memory[user.id] = user

    def exists_by_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def exists_by_user_name(self, user_name: str) -> bool:
        return self.get_by_username(user_name) is not None

class FakePasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return f'hashed::{password}'

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash(password)


class FakeTokenIssuer(TokenIssuer):
    def issue(self, user: User) -> str:
        return f'sub:{user.id}, roles:{[role.value for role in user.roles]}'

    def verify(self, token: str) -> UUID:
        sub = token.split(',')[0].removeprefix('sub:')
        return UUID(sub)
