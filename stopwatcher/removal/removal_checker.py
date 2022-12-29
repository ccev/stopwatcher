from __future__ import annotations

from .region import Region, ProtoCell
from stopwatcher.config import config

from typing import TYPE_CHECKING
from stopwatcher.fort import Game

if TYPE_CHECKING:
    from stopwatcher.fort import Fort


class RemovalChecker:
    def __init__(self):
        self.regions: dict[int, Region] = {}

    def check_forts(self, forts: list[Fort]) -> list[Fort]:
        session_regions: set[Region] = set()

        for fort in forts:
            if fort.region_id is None:
                continue

            if fort.game == Game.POGO:
                region: ProtoCell | None = self.regions.get(fort.region_id)

                if region is None:
                    region = ProtoCell.from_cell_id(fort.region_id)
                    self.regions[fort.region_id] = region

            else:
                continue

            # TODO limit how often regions are checked here
            region.add_to_session(fort)
            session_regions.add(region)

        removed_forts: list[Fort] = []
        for region in session_regions:
            removed_forts += region.check()

        return removed_forts
