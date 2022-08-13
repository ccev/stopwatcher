from __future__ import annotations

from typing import TYPE_CHECKING

from stopwatcher.watcher_jobs import ChangedLocationJob
from .base_processor import BaseProcessor, AnyProcessor
from .discord_sender import DiscordSender

if TYPE_CHECKING:
    from stopwatcher.db.accessor import DbAccessor
    from stopwatcher.watcher_jobs import AnyWatcherJob
    from stopwatcher.tileserver import Tileserver
    from stopwatcher.config import Area as AreaConfig


class AreaProcessor(BaseProcessor):
    def __init__(self, config: AreaConfig, accessor: DbAccessor, tileserver: Tileserver | None):
        self._config = config

        self._processors: list[AnyProcessor] = []
        for webhook_config in config.discord:
            self._processors.append(DiscordSender(config=webhook_config, tileserver=tileserver))

    async def process(self, job: AnyWatcherJob) -> None:
        if isinstance(job, ChangedLocationJob):
            if not (self._config.geofence.contains(job.old) or self._config.geofence.contains(job.new)):
                return
        elif not self._config.geofence.contains(job.fort.location):
            return

        for processor in self._processors:
            await processor.process(job)
