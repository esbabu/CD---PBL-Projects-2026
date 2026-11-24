import asyncio
from typing import Dict, List
from app.contracts.events import RunEvent


class EventBus:
    """
    Manages in-memory event distribution for runs.
    Enforces strictly monotonic per-run sequence numbers and fans out events to SSE subscriber queues.
    """

    def __init__(self):
        self._history: Dict[str, List[RunEvent]] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._seq_counters: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def publish(self, event: RunEvent) -> None:
        async with self._lock:
            run_id = event.run_id
            next_seq = self._seq_counters.get(run_id, 0) + 1
            self._seq_counters[run_id] = next_seq
            ordered_event = event.model_copy(update={"seq": next_seq})

            if run_id not in self._history:
                self._history[run_id] = []
            self._history[run_id].append(ordered_event)

            if run_id in self._subscribers:
                for queue in list(self._subscribers[run_id]):
                    try:
                        await queue.put(ordered_event)
                    except Exception:
                        pass

    async def subscribe(self, run_id: str) -> asyncio.Queue:
        async with self._lock:
            queue: asyncio.Queue = asyncio.Queue()
            if run_id not in self._subscribers:
                self._subscribers[run_id] = []
            self._subscribers[run_id].append(queue)

            # Replay existing history for this run so reconnects get full context
            if run_id in self._history:
                for past_event in self._history[run_id]:
                    await queue.put(past_event)

            return queue

    async def unsubscribe(self, run_id: str, queue: asyncio.Queue) -> None:
        async with self._lock:
            if run_id in self._subscribers:
                if queue in self._subscribers[run_id]:
                    self._subscribers[run_id].remove(queue)
                if not self._subscribers[run_id]:
                    del self._subscribers[run_id]

    def get_events(self, run_id: str) -> List[RunEvent]:
        return list(self._history.get(run_id, []))

    def clear_run(self, run_id: str) -> None:
        self._history.pop(run_id, None)
        self._subscribers.pop(run_id, None)
        self._seq_counters.pop(run_id, None)


# Global singleton event bus
event_bus = EventBus()
