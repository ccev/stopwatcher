from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypika import MySQLQuery

from stopwatcher.db.model.internal import fort_table
from stopwatcher.fort import Fort, FortType
from stopwatcher.log import log

if TYPE_CHECKING:
    from stopwatcher.db.accessor import DbAccessor


class FortHelper:
    @staticmethod
    def __fort_from_data(data: dict[str, Any]) -> Fort | None:
        try:
            fort_type = FortType(data.get(fort_table.type_id, 0))
        except ValueError:
            log.error(f"Unknown type id in your db. Entry: {data}")
            return None

        return Fort.from_db(data=data, fort_type=fort_type)

    @staticmethod
    async def get_forts_from_id(accessor: DbAccessor, id_: str) -> list[Fort]:
        query = MySQLQuery().from_(fort_table).select("*").where(fort_table.id == id_)
        result = await accessor.select_internal(query)

        if not result:
            return []

        forts = []
        for raw_fort in result:
            forts.append(FortHelper.__fort_from_data(raw_fort))

        return forts

    @staticmethod
    async def insert_fort(accessor: DbAccessor, fort: Fort) -> None:
        query = (
            MySQLQuery()
            .into(fort_table)
            .columns(
                fort_table.id,
                fort_table.game_id,
                fort_table.type_id,
                fort_table.lat,
                fort_table.lon,
                fort_table.name,
                fort_table.description,
                fort_table.cover_image,
            )
            .insert(
                fort.id,
                fort.game.value,
                fort.type.value,
                fort.location.lat,
                fort.location.lon,
                fort.name,
                fort.description,
                fort.cover_image,
            )
        )

        await accessor.commit_internal(query)

    @staticmethod
    async def delete_fort(accessor: DbAccessor, fort: Fort):
        query = (
            MySQLQuery()
            .from_(fort_table)
            .delete()
            .where(fort_table.id == fort.id)
            .where(fort_table.game_id == fort.game.value)
        )
        await accessor.commit_internal(query)

    @staticmethod
    async def update_fort(accessor: DbAccessor, fort: Fort):
        query = (
            MySQLQuery()
            .update(fort_table)
            .set(fort_table.type_id, fort.type.value)
            .set(fort_table.name, fort.name)
            .set(fort_table.description, fort.description)
            .set(fort_table.lat, fort.location.lat)
            .set(fort_table.lon, fort.location.lon)
            .set(fort_table.cover_image, fort.cover_image)
            .where(fort_table.id == fort.id)
            .where(fort_table.game_id == fort.game.value)
        )
        await accessor.commit_internal(query)
