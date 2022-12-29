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
        asyncio.create_task(self.read())

    async def _query_since(self, since: int):
        forts = await ExternalInputHelper.get_forts_since(self._db_accessor, since=since)
        log.info(f"Queried {len(forts)} Forts from external databases")
        self._out_queue.put_nowait(forts)

    async def read(self):
        delay = config.data_input.database_config.query_every
        await self._query_since(0)

        while True:
            await asyncio.sleep(delay)
            needed_time = int(time()) - delay - 20  # -20 to adjust for different delays that may happen
            await self._query_since(needed_time)
