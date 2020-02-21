# Beppu

Enum based asyncio syncronization primitive combining `asyncio.Event` and 
`enum.Enum`.

Code state is pre-alpha. :)

```python
from beppu import Basket

class FruitEnum(enum.Enum):
    ORANGE = enum.auto()
    APPLE = enum.auto()
    PEAR = enum.auto()
    BANANA = enum.auto()

basket = Basket(enum=Fruit)

async def eat_fruit_from_basket(basket, f):
    logger.debug(f"Waiting to eat {f}")
    await basket.wait_for(f)
    logger.debug(f"Ate a {f}")

async def shuffle_fruit(basket):
    seq = [1, 2, 4, 3]
    for i in seq:
        pick = Fruit(i)
        basket.pick(pick)
        logger.debug(f"Picking {pick} from {basket}")
        await asyncio.sleep(1)

tasks = [
    shuffle_fruit(basket),
    eat_fruit_from_basket(basket, Fruit(3)),
    eat_fruit_from_basket(basket, Fruit(4)),
]

await asyncio.gather(*tasks)

# output

[WARNING] | Picking FruitEnum.ORANGE from <beppu.Basket object at 0x10a9d8790> 
[INFO] | test_basket | Waiting to eat FruitEnum.PEAR 
[INFO] | test_basket | Waiting to eat FruitEnum.BANANA 
[WARNING] | test_basket | Picking FruitEnum.APPLE from <beppu.Basket object at 0x10a9d8790> 
[WARNING] | test_basket | Picking FruitEnum.BANANA from <beppu.Basket object at 0x10a9d8790> 
[INFO] | test_basket | Ate a FruitEnum.BANANA 
[WARNING] | test_basket | Picking FruitEnum.PEAR from <beppu.Basket object at 0x10a9d8790> 
[INFO] | test_basket | Ate a FruitEnum.PEAR 
```

## Installation

`Beppu` is available on pypi:

```bash
pip install beppu
```

