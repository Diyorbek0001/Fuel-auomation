from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from app.schemas.truck import TruckOut


class TruckBroadcaster:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict]] = set()

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=500)
        self._subscribers.add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._subscribers.discard(queue)

    def publish_truck(self, truck: TruckOut) -> None:
        self._publish({"type": "truck_update", "truck": truck.model_dump(mode="json")})

    def _publish(self, event: dict) -> None:
        stale: list[asyncio.Queue[dict]] = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                stale.append(queue)
        for queue in stale:
            self._subscribers.discard(queue)


truck_broadcaster = TruckBroadcaster()
