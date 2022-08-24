import pytest_asyncio

from app.contrib import MemoryRepository


@pytest_asyncio.fixture()
async def repo():
    repo = MemoryRepository(":memory:")
    await repo.connect()
    await repo.generate_schema()
    try:
        yield repo
    finally:
        await repo.close()
