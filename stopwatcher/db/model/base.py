from __future__ import annotations
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import TypeVar, Callable, TYPE_CHECKING, Any

from pypika import Table, Field
from pypika.queries import QueryBuilder

from stopwatcher.fort import Fort, FortType


class Base(Table, metaclass=ABCMeta):
    @property
    @abstractmethod
    def __table__(self) -> str:
        pass

    def __init__(self):
        for attr in self.__dir__():
            if attr == "__doc__":
                break
            if attr.startswith("__"):
                continue

            column = self.__getattribute__(attr)
            if not isinstance(column, Field):
                continue
            column.table = self

        super().__init__(self.__table__)


class FortBase(Base, metaclass=ABCMeta):
    id: Field
    lat: Field
    lon: Field
    name: Field
    description: Field
    cover_image: Field


AnyFortTable = TypeVar("AnyFortTable", bound=FortBase)


@dataclass
class ExternalInputDefinition:
    fort_factory: Callable[[dict[str, Any]], Fort]
    query: QueryBuilder
