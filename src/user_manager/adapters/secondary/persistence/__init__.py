from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from user_manager.adapters.secondary.persistence.mapper import (
    user_model_to_user,
    user_to_user_model,
)
from user_manager.adapters.secondary.persistence.models import UserModel
from user_manager.core.domain.exceptions import UserAlreadyExists, UserNotFound
from user_manager.core.domain.user import User
from user_manager.core.ports.secondary.user_repository import UserRepository


class SqlUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: UUID) -> User:
        user_in_db: UserModel | None = self.session.get(UserModel, user_id)

        if user_in_db is None:
            raise UserNotFound(f'user with id {user_id} not found')
        return user_model_to_user(user_in_db)

    def get_by_username(self, user_name: str) -> User:
        stmt = select(UserModel).where(UserModel.user_name == user_name)
        user_in_db: UserModel | None = self.session.scalars(stmt).one_or_none()

        if user_in_db is None:
            raise UserNotFound(f'user with user name {user_name}  found')

        return user_model_to_user(user_in_db)

    def get_by_email(self, email: str) -> User:
        stmt = select(UserModel).where(UserModel.email == email)

        user_in_db: UserModel | None = self.session.scalars(stmt).one_or_none()

        if user_in_db is None:
            raise UserNotFound(f'user with email {email} found')

        return user_model_to_user(user_in_db)

    def save(self, user: User) -> None:
        self.session.add(user_to_user_model(user))
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise UserAlreadyExists('This user already exists')

    def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel).where(UserModel.email == email)
        return self.session.scalars(stmt).one_or_none() is not None

    def exists_by_user_name(self, user_name: str) -> bool:
        stmt = select(UserModel).where(UserModel.user_name == user_name)
        return self.session.scalars(stmt).one_or_none() is not None
