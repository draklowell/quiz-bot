import pytest
from babel import Locale

from app.core import Repository, User, UserService

pytestmark = pytest.mark.asyncio

TEST_USER = {
    "telegram_id": 42,
    "first_name": "John",
    "last_name": "Pink",
    "username": "johnpink42",
    "language": Locale("en", "AU"),
}


async def test_resolve_user(repo: Repository):
    service = UserService(repo)

    user = User(1, **TEST_USER)

    assert (
        await service.resolve_user(
            user.telegram_id,
            user.language,
            user.first_name,
            user.last_name,
            user.username,
        )
        == user
    )

    user_model = await repo.get_user(user.id)
    assert user_model.id == user.id
    assert user_model.telegram_id == user.telegram_id
    assert user_model.first_name == user.first_name
    assert user_model.last_name == user.last_name
    assert user_model.username == user.username
