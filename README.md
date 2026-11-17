# beppu

An Enum-keyed async event. A `Basket` holds at most one member of an `Enum`, and
tasks wait until it holds the member they want. It runs on asyncio with no
dependencies, and on trio through [anyio](https://anyio.readthedocs.io).

```bash
pip install beppu          # asyncio
pip install 'beppu[anyio]'  # trio, or anyio's asyncio backend
```

Python 3.12 or later. On trio, install the `anyio` extra: without anyio, beppu uses
asyncio's `Event`, and trio rejects it.

## Usage

```python
import asyncio
from enum import Enum, auto

from beppu import Basket


class Light(Enum):
    RED = auto()
    AMBER = auto()
    GREEN = auto()


async def car(light: Basket[Light]) -> None:
    await light.wait_for(Light.GREEN)
    print("go")


async def pedestrian(light: Basket[Light]) -> None:
    match await light.wait_for_any(Light.RED, Light.AMBER):
        case Light.RED:
            print("cross")
        case Light.AMBER:
            print("wait at the kerb")


async def main() -> None:
    light = Basket(Light)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(car(light))
        tg.create_task(pedestrian(light))
        await asyncio.sleep(0)
        light.pick(Light.RED)  # the pedestrian crosses
        await asyncio.sleep(0)
        light.pick(Light.GREEN)  # the car goes


asyncio.run(main())
```

With the `anyio` extra, the same code written with `anyio.create_task_group()` and
`anyio.run(main, backend="trio")` runs on trio.

## API

`Basket(enum)` makes an empty basket for an `Enum` class. It can be created outside a
running event loop.

- `basket.value`: the member it holds, or `None` when it is empty.
- `basket.pick(member)`: hold `member` and wake the tasks waiting for it.
- `basket.clear()`: empty the basket.
- `await basket.wait_for(member)`: return once the basket holds `member`; at once if
  it already does.
- `await basket.wait_for_any(*members)`: return the member of `members` the basket
  holds, so you can `match` on it.

Waiting is level-triggered: a waiter returns only if the basket still holds its
member when the waiter resumes. If a member is picked and replaced before the waiter
gets to run, it keeps waiting.

Members are checked: anything that is not a member of the basket's `Enum` raises
`TypeError`. A basket over a `Flag` holds single members only; a combination such as
`Perm.R | Perm.W` raises `ValueError`.

### Timeouts

Waits have no timeout argument; use `asyncio.timeout()`, or anyio's cancel scopes:

```python
async with asyncio.timeout(5):  # raises TimeoutError
    await light.wait_for(Light.GREEN)

with anyio.move_on_after(5):
    await light.wait_for(Light.GREEN)

with anyio.fail_after(5):  # raises TimeoutError
    await light.wait_for(Light.GREEN)
```

## Development

```bash
uv sync
uv run ruff check && uv run ruff format --check && uv run pyright && uv run pytest
```

Tests run on asyncio and trio through anyio, and on asyncio with beppu's anyio-free
fallback. CI also runs `tests/smoke_asyncio.py` in an environment without anyio:

```bash
uv run --isolated --no-dev python tests/smoke_asyncio.py
```
