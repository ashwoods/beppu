"""An Enum-keyed async event: wait until a basket holds a given member."""

from enum import Enum

import anyio
import anyio.lowlevel

__all__ = ["Basket"]


class Basket[E: Enum]:
    """Holds at most one member of an Enum; tasks wait until it holds the one they want.

    Waiting is level-triggered: ``wait_for(X)`` returns once the basket holds ``X``
    when the waiting task resumes, not merely because ``X`` was picked at some point.
    Works on any backend anyio supports (asyncio and trio). For timeouts, wrap a
    wait in ``anyio.move_on_after()`` or ``anyio.fail_after()``.
    """

    __slots__ = ("_enum", "_events", "_value")

    def __init__(self, enum: type[E]) -> None:
        if not (isinstance(enum, type) and issubclass(enum, Enum)):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Basket needs an Enum class, got {enum!r}")
        self._enum = enum
        self._value: E | None = None
        # The event of a member is set exactly while the basket holds it. anyio
        # events cannot be cleared, so leaving a member swaps in a fresh one.
        self._events = {member: anyio.Event() for member in enum}

    def __repr__(self) -> str:
        return f"<{type(self).__name__}[{self._enum.__name__}] value={self._value!r}>"

    @property
    def value(self) -> E | None:
        """The member the basket holds, or None when it is empty."""
        return self._value

    def pick(self, member: E) -> None:
        """Put ``member`` in the basket and wake the tasks waiting for it."""
        member = self._check(member)
        if member is self._value:
            return
        self._leave()
        self._value = member
        self._events[member].set()

    def clear(self) -> None:
        """Empty the basket."""
        self._leave()
        self._value = None

    async def wait_for(self, member: E) -> None:
        """Wait until the basket holds ``member``; return at once if it already does."""
        member = self._check(member)
        while True:
            await self._events[member].wait()
            if self._value is member:
                return

    async def wait_for_any(self, *members: E) -> E:
        """Wait until the basket holds one of ``members`` and return that member."""
        if not members:
            raise TypeError("wait_for_any() needs at least one member")
        wanted = {self._check(member) for member in members}
        await anyio.lowlevel.checkpoint()
        while (value := self._value) is None or value not in wanted:
            async with anyio.create_task_group() as tg:
                for member in wanted:
                    tg.start_soon(
                        _cancel_when_set, self._events[member], tg.cancel_scope
                    )
        return value

    def _check(self, member: object) -> E:
        if not isinstance(member, self._enum):
            raise TypeError(
                f"expected a member of {self._enum.__name__}, got {member!r}"
            )
        if member not in self._events:
            raise ValueError(
                f"{member!r} is not a single member of {self._enum.__name__};"
                " a basket holds one member, not a combination of Flag members"
            )
        return member

    def _leave(self) -> None:
        if self._value is not None:
            self._events[self._value] = anyio.Event()


async def _cancel_when_set(event: anyio.Event, scope: anyio.CancelScope) -> None:
    await event.wait()
    scope.cancel()
