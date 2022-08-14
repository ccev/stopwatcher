from __future__ import annotations
from pypika import Field, CustomFunction, MySQLQuery
from typing import Any

from .base import FortBase, Base, ExternalInputDefinition
from stopwatcher.fort import Fort, FortType


UnixTimestamp = CustomFunction("UNIX_TIMESTAMP", ("datetime",))


class MadPokestop(FortBase):
    __table__ = "pokestop"

    id = Field("pokestop_id")
    lat = Field("latitude")
    lon = Field("longitude")
    name = Field("name")
    description = Field("description")
    cover_image = Field("url")
    last_modified = Field("last_modified")


mad_pokestop = MadPokestop()


class MadGym(Base):
    __table__ = "gym"

    id = Field("gym_id")
    lat = Field("latitude")
    lon = Field("longitude")
    last_modified = Field("last_modified")


class MadGymDetails(Base):
    __table__ = "gymdetails"

    id = Field("gym_id")
    name = Field("name")
    description = Field("description")
    cover_image = Field("url")


mad_gym = MadGym()
mad_gymdetails = MadGymDetails()


class MadSchema:
    @staticmethod
    def _pokestop_factory(data: dict[str, Any]) -> Fort:
        return Fort.from_db(table=mad_pokestop, fort_type=FortType.POKESTOP, data=data)

    @staticmethod
    def _gym_factory(data: dict[str, Any]) -> Fort:
        name = data.get(mad_gymdetails.name.name)
        if name == "unknown":
            name = None

        return Fort(
            id_=data[mad_gym.id.name],
            lat=data[mad_gym.lat.name],
            lon=data[mad_gym.lon.name],
            type_=FortType.GYM,
            name=name,
            description=data.get(mad_gymdetails.description.name),
            cover_image=data.get(mad_gymdetails.cover_image.name),
        )

    @staticmethod
    def get_forts(since: int) -> list[ExternalInputDefinition]:
        stops = ExternalInputDefinition(
            fort_factory=MadSchema._pokestop_factory,
            query=MySQLQuery.from_(mad_pokestop)
            .select("*")
            .where(UnixTimestamp(mad_pokestop.last_modified) > since),
        )
        gyms = ExternalInputDefinition(
            fort_factory=MadSchema._gym_factory,
            query=MySQLQuery()
            .from_(mad_gym)
            .left_join(mad_gymdetails)
            .on(mad_gym.id == mad_gymdetails.id)  # type: ignore
            .select(mad_gym.star, mad_gymdetails.star)
            .where(UnixTimestamp(mad_gym.last_modified) > since)
        )
        return [stops, gyms]


get_forts = MadSchema.get_forts
