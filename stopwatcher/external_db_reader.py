from __future__ import annotations

import asyncio
from time import time
from typing import TYPE_CHECKING

from .db.helper.external_input import ExternalInputHelper
from .log import log
from .config import config

if TYPE_CHECKING:
    from .db.accessor import DbAccessor


class ExternalDbReader:
    def __init__(self, accessor: DbAccessor, process_queue: asyncio.Queue):
        self._db_accessor: DbAccessor = accessor
        self._out_queue: asyncio.Queue = process_queue
        self._last_time: int = 0
        asyncio.create_task(self.read())

    async def read(self):
        while True:
            log.info(f"Querying external databases")
            new_time = int(time())
            forts = await ExternalInputHelper.get_forts_since(self._db_accessor, since=self._last_time)
            self._last_time = new_time

            self._out_queue.put_nowait(forts)
            await asyncio.sleep(config.data_input.database_config.query_every)
