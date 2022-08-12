from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
from asyncio import Queue

from .log import log
from .watcher_jobs import (
    AnyWatcherJob,
    NewFortJob,
    ChangedFortTypeJob,
    ChangedNameJob,
    ChangedDescriptionJob,
    ChangedLocationJob,
    ChangedCoverImageJob,
    NewFortDetailsJob,
)
from .processors import AnyProcessor, DiscordSender
from .config import config

if TYPE_CHECKING:
    from stopwatcher.tileserver import Tileserver


class JobWorker:
    def __init__(self, queue: Queue, tileserver: Tileserver | None):
        self._queue: "Queue[AnyWatcherJob]" = queue

        self._processors: list[AnyProcessor] = []
        for area in config.areas:
            for webhook_config in area.discord:
                self._processors.append(DiscordSender(config=webhook_config, tileserver=tileserver))

        asyncio.create_task(self.process_queue())

    async def process_queue(self):
        while True:
            job: AnyWatcherJob = await self._queue.get()
            log.info(f"Working on {job.__class__.__name__} for {job.fort}")

            for processor in self._processors:
                processor: AnyProcessor
                await processor.process(job)
