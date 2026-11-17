import asyncio

import pytest

import beppu


async def _sleep0() -> None:
    await asyncio.sleep(0)


@pytest.fixture(params=["asyncio", "trio", "asyncio-without-anyio"])
def anyio_backend(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> str:
    if request.param == "asyncio-without-anyio":
        # What beppu falls back to when anyio is not installed.
        monkeypatch.setattr(beppu, "Event", asyncio.Event)
        monkeypatch.setattr(beppu, "checkpoint", _sleep0)
        return "asyncio"
    return request.param
