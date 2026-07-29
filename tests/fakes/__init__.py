from uuid import UUID

from user_manager.core.domain.user import User
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.memory: dict[UUID, User] = {}

    def get_by_id(self, user_id: UUID) -> User | None:
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


class FakePasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return f'hashed::{password}'

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash(password)
