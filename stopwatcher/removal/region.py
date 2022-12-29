from __future__ import annotations

from time import time
from typing import TYPE_CHECKING

from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from stopwatcher.s2 import Cell

from protos import ClientMapCellProto

if TYPE_CHECKING:
    from stopwatcher.fort import Fort


class TrackedFort:
    def __init__(self, fort: Fort, now: float):
        self.fort: Fort = fort
        self.bad_counter: int = 0
        self.updated: float = now

        self._removed_before: bool = False

    @property
    def id(self) -> str:
        return self.fort.id

    def not_seen_now(self) -> None:
        self.bad_counter += 1

    def is_removed(self) -> bool:
        if self.bad_counter > 5 and not self._removed_before:  # TODO configure this
            self._removed_before = True
            return True
        return False

    def add_other_fort(self, fort: Fort, now: float) -> None:
        self.updated = now
        self.fort.add_other_fort(fort)


class Region(metaclass=ABCMeta):
    def __init__(self):
        self.tracked: dict[str, TrackedFort] = {}
        self.current_session: list[Fort] = []

    def add_to_session(self, fort: Fort) -> None:
        self.current_session.append(fort)

    @abstractmethod
    def check(self) -> list[Fort]:
        # update region with forts, return removed forts (if any)
        pass


class ProtoCell(Region):
    # used for tracking removals based on GMO Cells
    cell: Cell
    updated: float = 0

    @classmethod
    def from_cell_id(cls, cell_id: int) -> ProtoCell:
        self = cls()
        self.cell = Cell.from_cell_id(cell_id)
        return self

    def check(self) -> list[Fort]:
        if not self.current_session:
            return []

        self.updated = now = time()
        for fort in self.current_session:
            # if not self.cell.contains(fort.location):
            #     continue

            existing_fort = self.tracked.get(fort.id)
            if existing_fort is None:
                self.tracked[fort.id] = TrackedFort(fort, now)
            else:
                existing_fort.add_other_fort(fort, now)

        self.current_session.clear()
        removed_forts: list[Fort] = []
        bad_forts: list[TrackedFort] = [f for f in self.tracked.values() if f.updated < now]
        for bad_fort in bad_forts:
            bad_fort.not_seen_now()

            if bad_fort.is_removed():
                removed_forts.append(bad_fort.fort)

        return removed_forts
