import asyncio
import collections
import warnings


class Basket:
    def __init__(self, enum, loop=None):
        self.enum = enum
        self.waiters = {v: collections.deque() for v in enum}
        self.value = None
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
            warnings.warn(
                "The loop argument is deprecated since Python 3.8, "
                "and scheduled for removal in Python 3.10.",
                DeprecationWarning,
                stacklevel=2,
            )
        # for convenience reference enum values in the basket too
        for item in self.enum:
            setattr(self, item.name, item)

    @property
    def is_set(self):
        """Return True if and only if the basket has a value set."""
        return bool(self.value)

    def pick(self, member):
        """Set the internal value to valid enum value `member`. All coroutines
        waiting for it to be picked are awakened. Coroutine that call
        `wait_for` once the value has been picked will not block at all.
        """
        if member in self.enum:
            self.value = member
        else:
            raise ValueError("Invalid enum value")

        for fut in self.waiters[member]:
            if not fut.done():
                fut.set_result(True)

    async def wait_for(self, member):
        """Block until the internal flag is true.
        If the internal flag is true on entry, return True
        immediately.  Otherwise, block until another coroutine calls
        `pick` to set the flag to value, then return True.
        """
        if self.value == member:
            return True

        fut = self.loop.create_future()
        self.waiters[member].append(fut)
        try:
            await fut
            return True
        finally:
            self.waiters[member].remove(fut)

    async def wait_for_any(self):
        raise NotImplementedError

    async def wait_for_pick(self):
        raise NotImplementedError

    def clear(self):
        """Reset the internal flag to None. Subsequently, coroutines calling
        wait() will block until set() is called to the corresponding internal
        flag to true again."""
        self.value = None
