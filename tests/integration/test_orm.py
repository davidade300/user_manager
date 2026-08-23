import uuid

import pytest

from user_manager.adapters.secondary.persistence import (
    SqlUserRepository,
    UserModel,
    user_model_to_user,
    user_to_user_model,
)
from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    UserAlreadyExists,
    UsernameAlreadyInUse,
    UserNotFound,
)
from user_manager.core.domain.user import User
from user_manager.core.use_cases.register_user import RegisterUser

from ..fakes import FakePasswordHasher


class TestORM:
    def test_sql_repository_can_save_and_retrieve_user(
        self, db_session, regular_user
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        user = regular_user

        sql_repo.save(user)
        retrieved = sql_repo.get_by_id(regular_user.id)

        assert retrieved == regular_user

    def test_user_to_user_model_works(self, regular_user) -> None:
        user_model = user_to_user_model(regular_user)

        assert user_model.id == regular_user.id

    def test_user_model_to_user_works(self, db_session, regular_user) -> None:
        repo = SqlUserRepository(db_session)
        repo.save(regular_user)

        user_in_db = repo.session.get(UserModel, regular_user.id)
        assert user_in_db is not None
        user = user_model_to_user(user_in_db)

        assert user == regular_user

    def test_sql_repository_can_retrieve_user_by_email(
        self, db_session, regular_user
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        user = regular_user
        sql_repo.save(user)

        retrieved = sql_repo.get_by_email(regular_user.email)
        assert retrieved == regular_user

    def test_sql_repository_can_retrieve_user_by_user_name(
        self, db_session, regular_user
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        user = regular_user
        sql_repo.save(user)
        retrieved = sql_repo.get_by_username(regular_user.user_name)

        assert retrieved == regular_user

    def test_retrieving_user_by_id_wtith_wrong_id_raises(
        self, db_session, regular_user
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        sql_repo.save(regular_user)
        with pytest.raises(UserNotFound):
            sql_repo.get_by_id(uuid.uuid4())

    def test_retrieving_user_by_user_name_with_wrong_user_name_raises(
        self, db_session, regular_user
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        sql_repo.save(regular_user)
        with pytest.raises(UserNotFound):
            sql_repo.get_by_username('wrong_user_name')

    def test_saving_user_with_already_existing_user_name_raises(
        self, regular_user, db_session
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        sql_repo.save(regular_user)
        use_case = RegisterUser(sql_repo, FakePasswordHasher())

        with pytest.raises(UsernameAlreadyInUse):
            use_case.execute(
                full_name=regular_user.full_name,
                user_name=regular_user.user_name,
                email='different_email_1',
                date_of_birth=regular_user.date_of_birth,
                password=regular_user.password_hash,
            )

    def test_saving_user_with_already_existing_email_raises(
        self, regular_user, db_session
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        sql_repo.save(regular_user)
        use_case = RegisterUser(sql_repo, FakePasswordHasher())

        with pytest.raises(EmailAlreadyInUse):
            use_case.execute(
                full_name=regular_user.full_name,
                user_name='different_user_name_1',
                email=regular_user.email,
                date_of_birth=regular_user.date_of_birth,
                password=regular_user.password_hash,
            )

    def test_saving_duplicate_user_raises(
        self, db_session, regular_user
    ) -> None:
        sql_repo = SqlUserRepository(db_session)
        sql_repo.save(regular_user)
        duplicate_user = User.create(
            full_name=regular_user.full_name,
            user_name=regular_user.user_name,
            email=regular_user.email,
            date_of_birth=regular_user.date_of_birth,
            password_hash=regular_user.password_hash,
        )
        with pytest.raises(UserAlreadyExists):
            sql_repo.save(duplicate_user)
