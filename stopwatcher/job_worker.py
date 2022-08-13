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
    SetQueue
)
from .processors import AnyProcessor, DiscordSender, DbUpdater, AreaProcessor
from .config import config

if TYPE_CHECKING:
    from stopwatcher.tileserver import Tileserver
    from stopwatcher.db.accessor import DbAccessor


class JobWorker:
    def __init__(self, queue: SetQueue, tileserver: Tileserver | None, accessor: DbAccessor):
        self._queue: "SetQueue[AnyWatcherJob]" = queue

        self._processors: list[AnyProcessor] = []
        self._processors.append(DbUpdater(accessor))

        if not config.general.init:
            for area in config.areas:
                if area.geofence is None:
                    log.warning(f"Area {area.name} doesn't have a geofence defined. Not processing anything there")
                    continue

                self._processors.append(AreaProcessor(config=area, accessor=accessor, tileserver=tileserver))

        asyncio.create_task(self.process_queue())

    async def process_queue(self):
        while True:
            job: AnyWatcherJob = await self._queue.get()
            # log.info(f"Working on {job.__class__.__name__} for {job.fort}")

            for processor in self._processors:
                processor: AnyProcessor
                await processor.process(job)
