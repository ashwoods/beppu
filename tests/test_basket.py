import asyncio
import logging

import pytest

from beppu import Basket

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_basket_init(Fruit):
    basket = Basket(enum=Fruit)
    assert basket.BANANA == Fruit.BANANA
    assert basket.APPLE == Fruit.APPLE
    assert basket.PEAR == Fruit.PEAR
    assert basket.ORANGE == Fruit.ORANGE
    assert list(basket.waiters.keys()) == list(Fruit)
    assert basket.loop


@pytest.mark.asyncio
async def test_basket_events(Fruit):
    basket = Basket(enum=Fruit)

    async def eat_fruit_from_basket(basket, f):
        logger.info(f"Waiting to eat {f}")
        await basket.wait_for(f)
        logger.info(f"Ate a {f}")

    async def shuffle_fruit(basket):
        seq = [1, 2, 4, 3]
        for i in seq:
            pick = Fruit(i)
            basket.pick(pick)
            logger.warning(f"Picking {pick} from {basket}")
            await asyncio.sleep(1)

    tasks = [
        shuffle_fruit(basket),
        eat_fruit_from_basket(basket, Fruit(3)),
        eat_fruit_from_basket(basket, Fruit(4)),
    ]

    await asyncio.gather(*tasks)
