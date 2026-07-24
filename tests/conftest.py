from datetime import datetime, timezone, date
from typing import Any
from uuid import uuid4

import pytest

from user_manager.core.domain.user_role import UserRole


@pytest.fixture

def valid_user_data() -> dict[str, Any]:
    return {
        'id': uuid4(),
        'full_name': 'Test User',
        'user_name': 'fake_user_name',
        'email': 'fakemail@mail.com',
        'date_of_birth': date(2000, 8, 7),
        'password_hash': 'fake_password_hash',
        'is_active': True,
        'created_at': datetime(2026, 7, 24, tzinfo=timezone.utc),
        'updated_at': datetime(2026, 7, 24, tzinfo=timezone.utc),
        'roles': {UserRole.USER},
    }
