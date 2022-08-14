from __future__ import annotations

import asyncio
from typing import Dict, Any, List, NoReturn, Union, TYPE_CHECKING
from dataclasses import dataclass

import aiomysql
from pypika.queries import QueryBuilder

from stopwatcher.config import config

if TYPE_CHECKING:
    from stopwatcher.config import DbConnection


@dataclass
class ExternalInput:
    pool: aiomysql.Pool
    schema: str


class DbAccessor:
    internal_pool: aiomysql.Pool
    external_inputs: list[ExternalInput]

    @staticmethod
    def _connect_kwargs(connection: DbConnection) -> dict:
        return {
            "maxsize": 5,
            "host": connection.host,
            "port": connection.port,
            "user": connection.username,
            "password": connection.password,
            "db": connection.database,
        }

    async def connect(self, loop: asyncio.AbstractEventLoop):
        self.internal_pool = await aiomysql.create_pool(
            **self._connect_kwargs(config.stopwatcher_db),
            loop=loop,
        )

        self.external_inputs = []
        for external_connection in config.data_input.database:
            pool = await aiomysql.create_pool(
                **self._connect_kwargs(external_connection),
                loop=loop,
            )
            self.external_inputs.append(ExternalInput(pool=pool, schema=external_connection.db_schema))

    async def close(self):
        for pool in (self.internal_pool, *self.external_inputs):
            pool.close()
            await pool.wait_closed()

    @staticmethod
    async def basic_execute(
        pool: aiomysql.Pool, query: QueryBuilder, fetch: bool = True, commit: bool = False
    ) -> Union[None, List[Dict[str, Any]]]:
        r = None
        query = query.get_sql()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                cursor: aiomysql.DictCursor
                await cursor.execute(query)

                if commit:
                    await conn.commit()
                if fetch:
                    r = await cursor.fetchall()

        return r

    async def select_internal(self, query: QueryBuilder) -> list[dict[str, Any]]:
        return await self.basic_execute(self.internal_pool, query)

    async def select_any(self, query: QueryBuilder, pool: aiomysql.Pool) -> list[dict[str, Any]]:
        return await self.basic_execute(pool, query)

    async def commit_internal(self, query: QueryBuilder) -> NoReturn:
        await self.basic_execute(self.internal_pool, query, fetch=False, commit=True)
