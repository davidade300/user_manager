from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    DATABASE_URL: str = f'{getenv("DRIVERNAME")}://{getenv("USERNAME")}:{getenv("PASSWORD")}@{getenv("HOST")}/{getenv("DATABASE")}'
    TEST_DATABASE_URL: str = f'{getenv("TEST_DB")}'
