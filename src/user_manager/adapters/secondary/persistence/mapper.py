"""Translation between the ``User`` domain entity and its ORM model.

The heart of the "separate ORM model + mapper" approach: it keeps the domain
free of SQLAlchemy and the ORM model free of domain types. Two concerns live
only here — serializing ``roles`` (``set[UserRole]`` ↔ sorted ``list[str]``)
and re-attaching UTC to the timestamps on read, since the database returns
them naive.
"""

from datetime import UTC

from user_manager.adapters.secondary.persistence.models import UserModel
from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole


def user_to_user_model(user: User) -> UserModel:
    """Map a domain ``User`` to its ORM ``UserModel`` for persistence.

    Roles are serialized to a sorted list of their string values; timestamps
    pass through unchanged (the domain already produces UTC-aware ones).

    Args:
        user: The domain entity to translate.

    Returns:
        The equivalent ``UserModel`` ready to be persisted.
    """
    return UserModel(
        id=user.id,
        email=user.email,
        user_name=user.user_name,
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        password_hash=user.password_hash,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=sorted(role.value for role in user.roles),
    )


def user_model_to_user(user_model: UserModel) -> User:
    """Reconstitute a domain ``User`` from its ORM ``UserModel``.

    Roles are parsed from their string values back into ``UserRole`` members,
    and UTC is re-attached to the timestamps, which the database returns naive.

    Args:
        user_model: The ORM record loaded from the database.

    Returns:
        The equivalent domain ``User`` entity.
    """
    return User(
        id=user_model.id,
        email=user_model.email,
        user_name=user_model.user_name,
        full_name=user_model.full_name,
        date_of_birth=user_model.date_of_birth,
        password_hash=user_model.password_hash,
        is_active=user_model.is_active,
        created_at=user_model.created_at.replace(tzinfo=UTC),
        updated_at=user_model.updated_at.replace(tzinfo=UTC),
        roles={UserRole(role) for role in user_model.roles},
    )
