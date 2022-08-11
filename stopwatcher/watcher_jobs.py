from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from .fort import Fort, FortType
from .geo import Location


@dataclass
class _BaseWatcherJob:
    fort: Fort


AnyWatcherJob = TypeVar("AnyWatcherJob", bound=_BaseWatcherJob)


@dataclass
class NewFortJob(_BaseWatcherJob):
    pass


@dataclass
class NewFortDetailsJob(_BaseWatcherJob):
    pass


@dataclass
class RemovedFortJob(_BaseWatcherJob):
    pass


@dataclass
class _BaseEditJob(_BaseWatcherJob):
    old: str
    new: str


@dataclass
class ChangedFortTypeJob(_BaseEditJob):
    old: FortType
    new: FortType


@dataclass
class ChangedNameJob(_BaseEditJob):
    pass


@dataclass
class ChangedDescriptionJob(_BaseEditJob):
    pass


@dataclass
class ChangedLocationJob(_BaseEditJob):
    old: Location
    new: Location


@dataclass
class ChangedCoverImageJob(_BaseEditJob):
    pass
