from __future__ import annotations
from pypika import Field, MySQLQuery

from typing import Any
from .base import Base, ExternalInputDefinition, FortBase

from stopwatcher.fort import Fort, FortType


class RdmPokestop(FortBase):
    __table__ = "pokestop"

    id = Field("id")
    lat = Field("lat")
    lon = Field("lon")
    name = Field("name")
    description = Field("description")
    cover_image = Field("url")
    last_modified = Field("last_modified_timestamp")


rdm_pokestop = RdmPokestop()


class RdmGym(FortBase):
    __table__ = "gym"

    id = Field("id")
    lat = Field("lat")
    lon = Field("lon")
    name = Field("name")
    description = Field("description")
    cover_image = Field("url")
    last_modified = Field("last_modified_timestamp")


rdm_gym = RdmGym()


class RdmSchema:
    @staticmethod
    def _pokestop_factory(data: dict[str, Any]) -> Fort:
        return Fort.from_db(table=rdm_pokestop, fort_type=FortType.POKESTOP, data=data)

    @staticmethod
    def _gym_factory(data: dict[str, Any]) -> Fort:
        return Fort.from_db(table=rdm_gym, fort_type=FortType.GYM, data=data)

    @staticmethod
    def get_forts(since: int) -> list[ExternalInputDefinition]:
        stops = ExternalInputDefinition(
            fort_factory=RdmSchema._pokestop_factory,
            query=MySQLQuery.from_(rdm_pokestop).select("*").where(rdm_pokestop.last_modified > since)
        )
        gyms = ExternalInputDefinition(
            fort_factory=RdmSchema._gym_factory,
            query=MySQLQuery.from_(rdm_gym).select("*").where(rdm_gym.last_modified > since)
        )
        return [stops, gyms]


get_forts = RdmSchema.get_forts
