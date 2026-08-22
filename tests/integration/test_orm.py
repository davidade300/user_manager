from user_manager.adapters.secondary.persistence import (
    SqlUserRepository,
    UserModel,
    user_model_to_user,
    user_to_user_model,
)


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

    # TODO: adicionar testes para os bad paths.
