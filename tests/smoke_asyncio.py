"""Run beppu on plain asyncio in an environment without anyio installed."""

import asyncio
import sys
from enum import Enum, auto

from beppu import Basket


class Fruit(Enum):
    APPLE = auto()
    PEAR = auto()


basket = Basket(Fruit)  # outside a running loop
basket.pick(Fruit.PEAR)


async def main() -> None:
    basket.clear()
    waiter = asyncio.create_task(basket.wait_for_any(Fruit.APPLE))
    await asyncio.sleep(0)
    basket.pick(Fruit.APPLE)
    basket.pick(Fruit.PEAR)
    await asyncio.sleep(0)
    assert not waiter.done(), "wait_for_any must be level-triggered"
    basket.pick(Fruit.APPLE)
    assert await waiter is Fruit.APPLE
    try:
        async with asyncio.timeout(0):
            await basket.wait_for(Fruit.PEAR)
    except TimeoutError:
        pass  # expected: the timeout cancelled the wait
    else:
        raise AssertionError("the timeout did not cancel the wait")


asyncio.run(main())
assert "anyio" not in sys.modules, "anyio was imported"
print("beppu works on asyncio without anyio")
