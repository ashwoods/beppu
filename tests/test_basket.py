from enum import Enum, Flag, IntEnum, auto

import anyio
import pytest

from beppu import Basket


class Fruit(Enum):
    ORANGE = auto()
    APPLE = auto()
    PEAR = auto()


class Level(IntEnum):
    OFF = 0
    ON = 1


class Perm(Flag):
    R = auto()
    W = auto()


def test_pick_clear_and_repr() -> None:
    basket = Basket(Fruit)  # no event loop running
    assert basket.value is None
    assert repr(basket) == "<Basket[Fruit] value=None>"
    basket.pick(Fruit.APPLE)
    assert basket.value is Fruit.APPLE
    assert repr(basket) == "<Basket[Fruit] value=<Fruit.APPLE: 2>>"
    basket.clear()
    assert basket.value is None


def test_validation() -> None:
    with pytest.raises(TypeError, match="needs an Enum class"):
        Basket(int)  # type: ignore[type-var]
    basket = Basket(Fruit)
    with pytest.raises(TypeError, match="expected a member of Fruit"):
        basket.pick(2)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="expected a member of Fruit"):
        basket.pick(Level.ON)  # type: ignore[arg-type]
    assert basket.value is None


def test_flag_takes_single_members_only() -> None:
    basket = Basket(Perm)
    basket.pick(Perm.W)
    assert basket.value is Perm.W
    with pytest.raises(ValueError, match="not a single member of Perm"):
        basket.pick(Perm.R | Perm.W)
    assert basket.value is Perm.W


def test_falsy_member_counts_as_held() -> None:
    basket = Basket(Level)
    basket.pick(Level.OFF)
    assert basket.value is Level.OFF


@pytest.mark.anyio
async def test_wait_for_returns_at_once_when_held() -> None:
    basket = Basket(Fruit)
    basket.pick(Fruit.PEAR)
    with anyio.fail_after(1):
        await basket.wait_for(Fruit.PEAR)


@pytest.mark.anyio
async def test_wait_for_wakes_on_pick() -> None:
    basket = Basket(Fruit)
    woke: list[Fruit | None] = []

    async def waiter() -> None:
        await basket.wait_for(Fruit.APPLE)
        woke.append(basket.value)

    async with anyio.create_task_group() as tg:
        tg.start_soon(waiter)
        await anyio.wait_all_tasks_blocked()
        basket.pick(Fruit.ORANGE)
        await anyio.wait_all_tasks_blocked()
        assert woke == []
        basket.pick(Fruit.APPLE)
    assert woke == [Fruit.APPLE]


@pytest.mark.anyio
async def test_wait_for_is_level_triggered() -> None:
    basket = Basket(Fruit)
    woke: list[Fruit | None] = []

    async def waiter() -> None:
        await basket.wait_for(Fruit.APPLE)
        woke.append(basket.value)

    async with anyio.create_task_group() as tg:
        tg.start_soon(waiter)
        await anyio.wait_all_tasks_blocked()
        # APPLE comes and goes before the waiter runs: it keeps waiting.
        basket.pick(Fruit.APPLE)
        basket.pick(Fruit.PEAR)
        await anyio.wait_all_tasks_blocked()
        assert woke == []
        basket.clear()
        basket.pick(Fruit.APPLE)
    assert woke == [Fruit.APPLE]


@pytest.mark.anyio
async def test_wait_for_any_returns_the_member() -> None:
    basket = Basket(Fruit)
    got: list[Fruit] = []

    async def waiter() -> None:
        got.append(await basket.wait_for_any(Fruit.APPLE, Fruit.PEAR))

    async with anyio.create_task_group() as tg:
        tg.start_soon(waiter)
        await anyio.wait_all_tasks_blocked()
        basket.pick(Fruit.ORANGE)
        await anyio.wait_all_tasks_blocked()
        assert got == []
        basket.pick(Fruit.PEAR)
    assert got == [Fruit.PEAR]

    match await basket.wait_for_any(Fruit.ORANGE, Fruit.PEAR):
        case Fruit.PEAR:
            pass
        case other:
            pytest.fail(f"expected PEAR, got {other}")


@pytest.mark.anyio
async def test_wait_for_any_is_level_triggered() -> None:
    basket = Basket(Fruit)
    got: list[Fruit] = []

    async def waiter() -> None:
        got.append(await basket.wait_for_any(Fruit.APPLE, Fruit.PEAR))

    async with anyio.create_task_group() as tg:
        tg.start_soon(waiter)
        await anyio.wait_all_tasks_blocked()
        basket.pick(Fruit.APPLE)
        basket.pick(Fruit.ORANGE)
        await anyio.wait_all_tasks_blocked()
        assert got == []
        basket.pick(Fruit.PEAR)
    assert got == [Fruit.PEAR]


@pytest.mark.anyio
async def test_wait_for_any_validates() -> None:
    basket = Basket(Fruit)
    with pytest.raises(TypeError, match="at least one member"):
        await basket.wait_for_any()
    with pytest.raises(TypeError, match="expected a member of Fruit"):
        await basket.wait_for_any(Fruit.APPLE, Level.ON)  # type: ignore[arg-type]


@pytest.mark.anyio
async def test_timeouts_cancel_the_wait() -> None:
    basket = Basket(Fruit)
    with anyio.move_on_after(0) as scope:
        await basket.wait_for(Fruit.APPLE)
    assert scope.cancelled_caught
    with pytest.raises(TimeoutError):
        with anyio.fail_after(0):
            await basket.wait_for_any(Fruit.APPLE, Fruit.PEAR)
    # The basket still works after cancelled waits.
    basket.pick(Fruit.APPLE)
    assert await basket.wait_for_any(Fruit.APPLE, Fruit.PEAR) is Fruit.APPLE
