"""SQLAlchemy ORM models for the persistence adapter.

Part of the secondary (driven) persistence adapter. These models are the
relational representation of the domain and are deliberately kept separate
from the domain entities (the "separate ORM model + mapper" approach): the
domain never inherits from ``Base``, and translation between the two lives in
the mapper. The core never imports anything from this module.
"""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import BOOLEAN, JSON, TIMESTAMP, Date, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models in the persistence adapter."""


class UserModel(Base):
    """Relational mapping of the ``User`` domain entity.

    A "dumb" persistence record: it stores primitives only. In particular
    ``roles`` is a JSON array of role *strings* (not domain enums) — the mapper
    owns the translation to and from ``set[UserRole]``.
    """

    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    roles: Mapped[list[str]] = mapped_column(JSON, nullable=False)
