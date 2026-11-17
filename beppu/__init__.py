"""An Enum-keyed async event: wait until a basket holds a given member."""

from enum import Enum

try:
    from anyio import Event
    from anyio.lowlevel import checkpoint
except ImportError:  # without anyio, plain asyncio
    from asyncio import Event, sleep

    async def checkpoint() -> None:
        await sleep(0)


__all__ = ["Basket"]


class Basket[E: Enum]:
    """Holds at most one member of an Enum; tasks wait until it holds the one they want.

    Waiting is level-triggered: ``wait_for(X)`` returns once the basket holds ``X``
    when the waiting task resumes, not merely because ``X`` was picked at some point.
    Works on asyncio, and with anyio installed on any backend it supports (asyncio
    and trio). For timeouts, wrap a wait in ``asyncio.timeout()``, or in anyio's
    ``move_on_after()`` or ``fail_after()``.
    """

    __slots__ = ("_changed", "_enum", "_members", "_value")

    def __init__(self, enum: type[E]) -> None:
        if not (isinstance(enum, type) and issubclass(enum, Enum)):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Basket needs an Enum class, got {enum!r}")
        self._enum = enum
        self._members = frozenset(enum)
        self._value: E | None = None
        # Set whenever the value changes, then replaced by a fresh event: anyio
        # events cannot be cleared. Waiters recheck the value when it fires.
        self._changed = Event()

    def __repr__(self) -> str:
        return f"<{type(self).__name__}[{self._enum.__name__}] value={self._value!r}>"

    @property
    def value(self) -> E | None:
        """The member the basket holds, or None when it is empty."""
        return self._value

    def pick(self, member: E) -> None:
        """Put ``member`` in the basket and wake the tasks waiting for it."""
        member = self._check(member)
        if member is not self._value:
            self._change(member)

    def clear(self) -> None:
        """Empty the basket."""
        if self._value is not None:
            self._change(None)

    async def wait_for(self, member: E) -> None:
        """Wait until the basket holds ``member``; return at once if it already does."""
        await self.wait_for_any(member)

    async def wait_for_any(self, *members: E) -> E:
        """Wait until the basket holds one of ``members`` and return that member."""
        if not members:
            raise TypeError("wait_for_any() needs at least one member")
        wanted = {self._check(member) for member in members}
        await checkpoint()
        while (value := self._value) is None or value not in wanted:
            await self._changed.wait()
        return value

    def _change(self, value: E | None) -> None:
        self._value = value
        changed, self._changed = self._changed, Event()
        changed.set()

    def _check(self, member: object) -> E:
        if not isinstance(member, self._enum):
            raise TypeError(
                f"expected a member of {self._enum.__name__}, got {member!r}"
            )
        if member not in self._members:
            raise ValueError(
                f"{member!r} is not a single member of {self._enum.__name__};"
                " a basket over a Flag holds one non-zero member at a time"
            )
        return member
