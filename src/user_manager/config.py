from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    DATABASE_URL: str = f'{getenv("DRIVERNAME")}://{getenv("USERNAME")}:{getenv("PASSWORD")}@{getenv("HOST")}/{getenv("DATABASE")}'
    TEST_DATABASE_URL: str = f'{getenv("TEST_DB")}'
    JWT_SECRET_KEY: str = getenv('JWT_SECRET_KEY', '')
    JWT_ALGORITHM: str = getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_MINUTES: int = int(getenv('JWT_EXPIRATION_MINUTES', '60'))
