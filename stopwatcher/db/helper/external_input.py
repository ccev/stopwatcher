from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pypika import MySQLQuery

from stopwatcher.db.model.rdm import get_forts as rdm_get
from stopwatcher.db.model.mad import get_forts as mad_get
from stopwatcher.fort import Fort, FortType, Game
from stopwatcher.log import log

if TYPE_CHECKING:
    from stopwatcher.db.accessor import DbAccessor
    from stopwatcher.tileserver.staticmap import Bounds
    from stopwatcher.db.model.base import ExternalInputDefinition


SCHEMAS: dict[str, Callable[[int], list[ExternalInputDefinition]]] = {
    "rdm": rdm_get,
    "mad": mad_get
}


class ExternalInputHelper:
    @staticmethod
    async def get_forts_since(accessor: DbAccessor, since: int):
        forts: list[Fort] = []
        for external in accessor.external_inputs:
            get_method = SCHEMAS.get(external.schema)

            if get_method is None:
                log.warning(f"Unknown schema in config: {external.schema}")
                continue

            definitions = get_method(since)
            for definition in definitions:
                result = await accessor.select_any(definition.query, external.pool)
                for raw_fort in result:
                    forts.append(definition.fort_factory(raw_fort))

        return forts
