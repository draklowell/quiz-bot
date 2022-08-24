import pytest

from app.contrib import MemoryRepository

pytestmark = pytest.mark.asyncio


async def test_generate_constraints():
    constraints, values = MemoryRepository._generate_constraints(
        a=object, b=None, c="test"
    )
    assert constraints == ["`a`", "?", "?"]
    assert values == [None, "test"]
