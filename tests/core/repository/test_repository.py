import pytest

from .memory import MemoryRepository

pytestmark = pytest.mark.asyncio


async def test_transaction():
    class Mock(MemoryRepository):
        async def begin_transaction(self):
            nonlocal begun
            begun = True

        async def cancel_transaction(self):
            nonlocal canceled
            canceled = True

        async def commit_transaction(self):
            nonlocal commited
            commited = True

    begun = False
    canceled = False
    commited = False

    repo = Mock()
    async with repo.transaction():
        assert begun
        pass

    assert not canceled
    assert commited

    begun = False
    canceled = False
    commited = False

    repo = Mock()
    try:
        async with repo.transaction():
            assert begun
            raise ZeroDivisionError()
    except ZeroDivisionError:
        pass

    assert canceled
    assert not commited
