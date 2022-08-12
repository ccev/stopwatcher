from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from .fort import Fort, FortType
from .geo import Location


@dataclass
class _BaseWatcherJob:
    __key__ = ""

    fort: Fort


AnyWatcherJob = TypeVar("AnyWatcherJob", bound=_BaseWatcherJob)


@dataclass
class NewFortJob(_BaseWatcherJob):
    __key__ = "new"


@dataclass
class NewFortDetailsJob(_BaseWatcherJob):
    __key__ = "new_details"


@dataclass
class RemovedFortJob(_BaseWatcherJob):
    __key__ = "removed"


@dataclass
class _BaseEditJob(_BaseWatcherJob):
    old: str
    new: str


@dataclass
class ChangedFortTypeJob(_BaseEditJob):
    __key__ = "conversion"

    old: FortType
    new: FortType


@dataclass
class ChangedNameJob(_BaseEditJob):
    __key__ = "edit_name"


@dataclass
class ChangedDescriptionJob(_BaseEditJob):
    __key__ = "edit_description"


@dataclass
class ChangedLocationJob(_BaseEditJob):
    __key__ = "edit_location"

    old: Location
    new: Location


@dataclass
class ChangedCoverImageJob(_BaseEditJob):
    __key__ = "edit_cover"
