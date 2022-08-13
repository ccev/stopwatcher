from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar
from asyncio import Queue

from .fort import Fort, FortType
from .geo import Location


class SetQueue(Queue):
    def _init(self, maxsize):
        self._queue = set()

    def _put(self, item):
        self._queue.add(item)

    def _get(self):
        return self._queue.pop()


@dataclass(eq=False)
class _BaseWatcherJob:
    __key__ = ""

    fort: Fort

    def __hash__(self):
        return hash((self.fort.id, self.fort.type.value, self.__class__))

    def __eq__(self, other: AnyWatcherJob):
        return self.fort.id == other.fort.id and self.fort.type == other.fort.type and self.__class__ == other.__class__


AnyWatcherJob = TypeVar("AnyWatcherJob", bound=_BaseWatcherJob)


@dataclass(eq=False)
class NewFortJob(_BaseWatcherJob):
    __key__ = "new"


@dataclass(eq=False)
class NewFortDetailsJob(_BaseWatcherJob):
    __key__ = "new_details"


@dataclass(eq=False)
class RemovedFortJob(_BaseWatcherJob):
    __key__ = "removed"


@dataclass(eq=False)
class BaseEditJob(_BaseWatcherJob):
    old: str
    new: str


@dataclass(eq=False)
class ChangedFortTypeJob(BaseEditJob):
    __key__ = "conversion"

    old: FortType
    new: FortType


@dataclass(eq=False)
class ChangedNameJob(BaseEditJob):
    __key__ = "edit_name"


@dataclass(eq=False)
class ChangedDescriptionJob(BaseEditJob):
    __key__ = "edit_description"


@dataclass(eq=False)
class ChangedLocationJob(BaseEditJob):
    __key__ = "edit_location"

    old: Location
    new: Location


@dataclass(eq=False)
class ChangedCoverImageJob(BaseEditJob):
    __key__ = "edit_cover"
