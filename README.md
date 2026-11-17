# beppu

An Enum-keyed async event. A `Basket` holds at most one member of an `Enum`, and
tasks wait until it holds the member they want. It runs on
[anyio](https://anyio.readthedocs.io), so it works with asyncio and trio.

```bash
pip install beppu
```

Python 3.12 or later.

## Usage

```python
from enum import Enum, auto

import anyio
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
    async with anyio.create_task_group() as tg:
        tg.start_soon(car, light)
        tg.start_soon(pedestrian, light)
        await anyio.wait_all_tasks_blocked()
        light.pick(Light.RED)  # the pedestrian crosses
        await anyio.wait_all_tasks_blocked()
        light.pick(Light.GREEN)  # the car goes


anyio.run(main)
```

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

Waits have no timeout argument; use anyio's cancel scopes:

```python
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

Tests run on both asyncio and trio.
