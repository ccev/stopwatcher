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
class BaseEditJob(_BaseWatcherJob):
    old: str
    new: str


@dataclass
class ChangedFortTypeJob(BaseEditJob):
    __key__ = "conversion"

    old: FortType
    new: FortType


@dataclass
class ChangedNameJob(BaseEditJob):
    __key__ = "edit_name"


@dataclass
class ChangedDescriptionJob(BaseEditJob):
    __key__ = "edit_description"


@dataclass
class ChangedLocationJob(BaseEditJob):
    __key__ = "edit_location"

    old: Location
    new: Location


@dataclass
class ChangedCoverImageJob(BaseEditJob):
    __key__ = "edit_cover"
