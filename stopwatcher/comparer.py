from __future__ import annotations

import asyncio
from asyncio import Queue
from typing import TYPE_CHECKING

from .db.helper.internal_fort import FortHelper
from .fort import Fort, Game
from .watcher_jobs import (
    AnyWatcherJob,
    NewFortJob,
    ChangedFortTypeJob,
    ChangedNameJob,
    ChangedDescriptionJob,
    ChangedLocationJob,
    ChangedCoverImageJob,
    NewFortDetailsJob,
    SetQueue,
    RemovedFortJob,
)
from .s2 import Cell
from .removal.removal_checker import RemovalChecker

if TYPE_CHECKING:
    from .db.accessor import DbAccessor


class FortComparer:
    def __init__(self, accessor: DbAccessor, inbound_queue: Queue, outbound_queue: SetQueue):
        self._db_accessor: DbAccessor = accessor
        self._in_queue: "Queue[list[Fort]]" = inbound_queue
        self._out_queue: "SetQueue[AnyWatcherJob]" = outbound_queue
        self._removal_checker: RemovalChecker = RemovalChecker()
        asyncio.create_task(self.compare())

    def _add_job(self, job: AnyWatcherJob):
        self._out_queue.put_nowait(job)

    async def compare(self):
        while True:
            forts = await self._in_queue.get()

            if not forts:
                continue

            removed_forts = self._removal_checker.check_forts(forts)
            for removed_fort in removed_forts:
                self._add_job(RemovedFortJob(removed_fort))

            for fort in forts:
                db_forts = await FortHelper.get_forts_from_id(accessor=self._db_accessor, id_=fort.id)
                same_fort = next((f for f in db_forts if f.type == fort.type), None)

                if same_fort is None:
                    same_game_fort = next((f for f in db_forts if f.game == fort.game), None)

                    if same_game_fort is None:
                        self._add_job(NewFortJob(fort))
                    else:
                        fort.add_other_fort(same_game_fort)
                        self._add_job(ChangedFortTypeJob(fort, old=same_game_fort.type, new=fort.type))

                    continue

                if same_fort.name is None and fort.name is not None:
                    self._add_job(NewFortDetailsJob(fort))
                else:
                    fort.add_other_fort(same_fort)

                    def compare_str(attr: str):
                        return (not getattr(same_fort, attr) and getattr(fort, attr)) or (
                            getattr(fort, attr)
                            and getattr(same_fort, attr)
                            and getattr(same_fort, attr).strip() != getattr(fort, attr).strip()
                        )

                    if compare_str("name"):
                        self._add_job(ChangedNameJob(fort, old=same_fort.name, new=fort.name))

                    if compare_str("description"):
                        self._add_job(ChangedDescriptionJob(fort, old=same_fort.description, new=fort.description))

                    if fort.location != same_fort.location:
                        self._add_job(ChangedLocationJob(fort, old=same_fort.location, new=fort.location))

                    if compare_str("cover_image"):
                        self._add_job(ChangedCoverImageJob(fort, old=same_fort.cover_image, new=fort.cover_image))
