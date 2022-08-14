from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from stopwatcher.config import config
from stopwatcher.db.model.mad import get_forts as mad_get
from stopwatcher.db.model.rdm import get_forts as rdm_get
from stopwatcher.fort import Fort, Game
from stopwatcher.log import log
from .internal_fort import FortHelper

if TYPE_CHECKING:
    from stopwatcher.db.accessor import DbAccessor
    from stopwatcher.db.model.base import ExternalInputDefinition


SCHEMAS: dict[str, Callable[[int], list[ExternalInputDefinition]]] = {"rdm": rdm_get, "mad": mad_get}

GAMES: dict[str, Game] = {"rdm": Game.POGO, "mad": Game.POGO}


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
            this_forts: list[Fort] = []
            for definition in definitions:
                result = await accessor.select_any(definition.query, external.pool)

                for raw_fort in result:
                    this_forts.append(definition.fort_factory(raw_fort))

            if not this_forts:
                continue

            fort_ids = [f.id for f in this_forts]
            game = GAMES[external.schema]
            existing_count = await FortHelper.get_fort_count_for_id(accessor, game=game, ids=fort_ids)
            missing_forts = len(fort_ids) - existing_count
            if missing_forts > config.data_input.database_config.difference_threshold:
                log.warning(
                    f"There are {missing_forts} forts in an external database that would be processed. "
                    f"Instead, they will be skipped and copied directly"
                )

                await FortHelper.insert_forts(accessor, this_forts, insert_ignore=True)
            else:
                forts += this_forts

        return forts
