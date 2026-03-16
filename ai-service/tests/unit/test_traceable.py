import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.observability.traceable import traceable


def test_traceable_supports_async_function():
    @traceable(name="unit_async_trace", run_type="chain")
    async def sample_async(value: int) -> int:
        return value + 1

    result = asyncio.run(sample_async(1))
    assert result == 2


def test_traceable_supports_sync_function():
    @traceable(name="unit_sync_trace", run_type="chain")
    def sample_sync(value: int) -> int:
        return value + 1

    result = sample_sync(1)
    assert result == 2
