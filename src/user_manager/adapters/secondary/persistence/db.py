from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from user_manager.config import Settings

engine: Engine = create_engine(
    url=Settings.DATABASE_URL,
    echo=True,  # TODO: remover isso
)
SESSION_FACTORY: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autoflush=True,
)


@contextmanager
def get_session() -> Generator[Session]:
    session: Session = SESSION_FACTORY()
    try:
        yield session
    finally:
        session.close()
