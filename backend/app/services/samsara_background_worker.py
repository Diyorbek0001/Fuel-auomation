from __future__ import annotations

import asyncio
from contextlib import suppress

from app.core.config import get_settings
from app.db.session import async_session_maker
from app.services.samsara_sync_service import sync_all_samsara_accounts


class SamsaraBackgroundWorker:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._stop_event: asyncio.Event | None = None

    def start(self) -> None:
        settings = get_settings()
        if self._task is not None or not settings.samsara_accounts:
            return
        self._stop_event = asyncio.Event()
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(), name="samsara-background-worker")

    async def stop(self) -> None:
        if self._task is None:
            return
        if self._stop_event is not None:
            self._stop_event.set()
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None
        self._stop_event = None

    async def _run(self) -> None:
        settings = get_settings()
        interval = max(15, settings.samsara_poll_interval_seconds)
        if self._stop_event is None:
            return
        while not self._stop_event.is_set():
            try:
                async with async_session_maker() as session:
                    await sync_all_samsara_accounts(session)
            except Exception:
                pass
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue


samsara_background_worker = SamsaraBackgroundWorker()
