import heapq
import asyncio

from contextlib import asynccontextmanager

from src.Constants import Constants as C

class AsyncSlotsManager:
    """Manages Slots Asynchronously, while limiting the amount of slots that can be used at a time, when all slots are occupied, new tasks are added to a waiting list"""

    def __init__(self, maxSlots):
        self.free = maxSlots
        self.waiting = []  # heap of tuples (priority, arrival number, future)
        self.arrivals = 0

    @asynccontextmanager
    async def UseSlot(self, priority=C.NOW):
        """Tries to use a free slot, there is no free slots available it puts it into a waiting list and order it according to its priority(the smaller the number the
        higher the priority), if two elements have the same priority the element that arrived first will be first on the waiting list.

        priority: an int variable signifying the priority, the smaller it is the higher the priority.
        """

        if self.free > 0 and not self.waiting:
            self.free -= 1
        else:
            future = asyncio.get_running_loop().create_future()
            self.arrivals += 1
            heapq.heappush(self.waiting, (priority, self.arrivals, future))
            try:
                await future # wait until this future's(task's) turn
            except asyncio.CancelledError:
                if future.done() and not future.cancelled():
                    self.Release()  # the slot was handed over just as this task was cancelled, here we skip it
                raise
        try:
            yield # start doing the task
        finally:
            self.Release()

    def Release(self):
        """Starts the next task that is waiting, if there is no task waiting, it gives back a slot."""

        while self.waiting:
            future = heapq.heappop(self.waiting)[2]
            if not future.done():  # if the future was not canceled, if it was we skip it.
                future.set_result(True) #release the future (set it to done), this will allow its belonging task to run
                return

        self.free += 1