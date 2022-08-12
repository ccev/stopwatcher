from __future__ import annotations

from .base_processor import BaseProcessor
from stopwatcher.db.accessor import DbAccessor
from stopwatcher.db.helper.internal_fort import FortHelper
from stopwatcher.watcher_jobs import (
    AnyWatcherJob,
    NewFortJob,
    RemovedFortJob,
    ChangedFortTypeJob,
    ChangedNameJob,
    ChangedDescriptionJob,
    ChangedLocationJob,
    ChangedCoverImageJob,
    NewFortDetailsJob,
BaseEditJob
)
from stopwatcher.log import log


class DbUpdater(BaseProcessor):
    def __init__(self, accessor: DbAccessor):
        self._db_accessor: DbAccessor = accessor

    async def process(self, job: AnyWatcherJob) -> None:
        if isinstance(job, NewFortJob):
            log.info(f"New {job.fort}. Inserting into db")
            await FortHelper.insert_fort(self._db_accessor, job.fort)
        elif isinstance(job, RemovedFortJob):
            log.info(f"{job.fort} got removed. Deleting from db")
            await FortHelper.delete_fort(self._db_accessor, job.fort)
        elif isinstance(job, NewFortDetailsJob) or isinstance(job, BaseEditJob):
            log.info(f"{job.fort} changed. Updating in db")
            await FortHelper.update_fort(self._db_accessor, job.fort)
            # TODO if there's multiple changes at once, it shouldn't update for each of them
