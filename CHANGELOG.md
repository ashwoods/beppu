# Changelog

## 0.1.0

A rewrite. **Breaking:** code written for 0.0.1 needs changes.

- Requires Python 3.12 or later, and runs on anyio: asyncio and trio both work.
- `Basket` is generic over its Enum: `Basket(Fruit)` is a `Basket[Fruit]`, and the
  package ships type information (`py.typed`).
- `Basket(enum)` takes no `loop` argument and can be created outside a running loop.
- Members are no longer copied onto the basket: write `Fruit.APPLE`, not
  `basket.APPLE`. The `enum` and `waiters` attributes are gone.
- `is_set` is gone: check `basket.value is not None`. (It was false for a held
  member with a falsy value, such as an `IntEnum` member `0`.)
- `pick()` raises `TypeError` for anything that is not a member of the basket's
  Enum, and `ValueError` for combined `Flag` values.
- `wait_for()` returns `None` instead of `True`, and is level-triggered: it returns
  only while the basket holds the member, not after it has moved on.
- `wait_for_any(*members)` is implemented and returns the member the basket holds.
  The `wait_for_pick()` stub is removed.
- `clear()` empties the basket; waiters for the member it held keep waiting.
- Packaging moved to `pyproject.toml` (hatchling) and uv; tox, Travis and flake8 are
  replaced by ruff, pyright and GitHub Actions.

## 0.0.1

First prototype.
