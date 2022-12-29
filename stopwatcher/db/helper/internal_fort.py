from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypika import MySQLQuery
from pypika.terms import Values
from pypika.functions import Count

from stopwatcher.db.model.internal import fort_table
from stopwatcher.fort import Fort, FortType, Game
from stopwatcher.log import log

if TYPE_CHECKING:
    from stopwatcher.db.accessor import DbAccessor
    from stopwatcher.tileserver.staticmap import Bounds
    from stopwatcher.geo import Geofence


class FortHelper:
    @staticmethod
    def __fort_from_data(data: dict[str, Any]) -> Fort | None:
        try:
            fort_type = FortType(data.get(fort_table.type_id.name, 0))
        except ValueError:
            log.error(f"Unknown type id in your db. Entry: {data}")
            return None

        return Fort.from_db(table=fort_table, fort_type=fort_type, data=data)

    @staticmethod
    def __fort_list_from_data(result: list[dict[str, Any]]) -> list[Fort]:
        forts = []
        for raw_fort in result:
            fort = FortHelper.__fort_from_data(raw_fort)
            if fort is not None:
                forts.append(fort)

        return forts

    @staticmethod
    async def get_forts_from_id(accessor: DbAccessor, id_: str) -> list[Fort]:
        query = MySQLQuery().from_(fort_table).select("*").where(fort_table.id == id_)
        result = await accessor.select_internal(query)
        return FortHelper.__fort_list_from_data(result)

    @staticmethod
    async def insert_fort(accessor: DbAccessor, fort: Fort) -> None:
        await FortHelper.insert_forts(accessor, [fort])

    @staticmethod
    def __pypika_sql_injection(arg: str | None):
        if arg is None:
            return None
        return arg.replace("\\'", "'")

    @staticmethod
    async def insert_forts(accessor: DbAccessor, forts: list[Fort], insert_ignore: bool = False):
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
        )

        for fort in forts:
            query = query.insert(
                fort.id,
                fort.game.value,
                fort.type.value,
                fort.location.lat,
                fort.location.lon,
                FortHelper.__pypika_sql_injection(fort.name),
                FortHelper.__pypika_sql_injection(fort.description),
                fort.cover_image,
            )

        if insert_ignore:
            query = query.ignore()
            query = query.on_duplicate_key_update(fort_table.id, Values(fort_table.id))

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
            .set(fort_table.lat, fort.location.lat)
            .set(fort_table.lon, fort.location.lon)
            .where(fort_table.id == fort.id)
            .where(fort_table.game_id == fort.game.value)
        )
        if fort.name is not None:
            query = query.set(fort_table.name, fort.name)
        if fort.description is not None:
            query = query.set(fort_table.description, fort.description)
        if fort.cover_image is not None:
            query = query.set(fort_table.cover_image, fort.cover_image)
        await accessor.commit_internal(query)

    @staticmethod
    async def get_forts_in_bounds(accessor: DbAccessor, bounds: Bounds, game: Game) -> list[Fort]:
        query = (
            MySQLQuery()
            .from_(fort_table)
            .select("*")
            .where(fort_table.lat[bounds.min.lat : bounds.max.lat])
            .where(fort_table.lon[bounds.min.lon : bounds.max.lon])
            .where(fort_table.game_id == game.value)
        )
        result = await accessor.select_internal(query)
        return FortHelper.__fort_list_from_data(result)

    @staticmethod
    async def get_fort_count_for_id(accessor: DbAccessor, game: Game, ids: list[str]) -> int:
        query = (
            MySQLQuery()
            .from_(fort_table)
            .select(Count("*"))
            .where(fort_table.game_id == game.value)
            .where(fort_table.id.isin(ids))
        )
        result = await accessor.select_internal(query)
        _, count = result[0].popitem()
        return count

    @staticmethod
    async def get_forts_from_geofence(accessor: DbAccessor, game: Game, geofence: Geofence) -> list[Fort]:
        bounds = geofence.bounds()
        query = (
            MySQLQuery()
            .from_(fort_table)
            .select("*")
            .where(fort_table.game_id == game.value)
            .where(fort_table.lat[bounds.min.lat:bounds.max.lat])
            .where(fort_table.lon[bounds.min.lon:bounds.max.lon])
        )
        result = await accessor.select_internal(query)
        forts = []

        for fort in FortHelper.__fort_list_from_data(result):
            if geofence.contains(fort.location):
                forts.append(fort)
        return forts
