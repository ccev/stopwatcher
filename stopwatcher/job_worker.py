from __future__ import annotations

import asyncio
from asyncio import Queue

from .log import log
from .watcher_jobs import (
    AnyWatcherJob,
)


class JobWorker:
    def __init__(self, queue: Queue):
        self._queue: "Queue[AnyWatcherJob]" = queue
        asyncio.create_task(self.process_queue())

    async def process_queue(self):
        while True:
            job: AnyWatcherJob = await self._queue.get()
            log.info(f"Working on {job.__class__.__name__} for {job.fort}")
