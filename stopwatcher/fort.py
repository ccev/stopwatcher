from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any
from protos import PokemonFortProto, FortType as ProtoFortType, FortDetailsOutProto

from .db.model.internal import fort_table
from .geo import Location

if TYPE_CHECKING:
    from .accepter import FortRequest


class Game(Enum):
    UNKNOWN = 0
    POGO = 10
    INGRESS = 20
    LIGHTSHIP = 30


class FortType(Enum):
    UNKNOWN = 0
    GYM = 10
    POKESTOP = 15
    PORTAL = 20
    LIGHTSHIP_POI = 30

    @classmethod
    def from_proto_type(cls, proto: ProtoFortType):
        if proto == ProtoFortType.GYM:
            return FortType.GYM
        return FortType.POKESTOP


class Fort:
    def __init__(
        self,
        id_: str,
        lat: float,
        lon: float,
        type_: FortType = FortType.UNKNOWN,
        name: str | None = None,
        description: str | None = None,
        cover_image: str | None = None,
    ):
        self.id: str = id_
        self.location: Location = Location(lat=lat, lon=lon)
        self.type: FortType = type_
        self.game: Game = self.game_from_type(self.type)

        self.name: str | None = name
        self.description: str | None = description
        self.cover_image: str | None = cover_image

    def __repr__(self):
        rep = f"{self.type.name.title()}("
        if self.name is not None:
            rep += f"name='{self.name}', "
        return rep + f"id={self.id})"

    @classmethod
    def from_request(cls, request: FortRequest, fort_type: FortType):
        return cls(
            id_=request.id,
            lat=request.lat,
            lon=request.lon,
            type_=fort_type,
            name=request.name,
            description=request.description,
            cover_image=request.cover_image,
        )

    @classmethod
    def from_db(cls, data: dict[str, Any], fort_type: FortType):
        return cls(
            id_=data[fort_table.id.name],
            lat=data[fort_table.lat.name],
            lon=data[fort_table.lon.name],
            type_=fort_type,
            name=data.get(fort_table.name.name),
            description=data.get(fort_table.description.name),
            cover_image=data.get(fort_table.cover_image.name),
        )

    @classmethod
    def from_fort_proto(cls, proto: PokemonFortProto):
        return cls(
            id_=proto.fort_id,
            lat=proto.latitude,
            lon=proto.longitude,
            type_=FortType.from_proto_type(proto.fort_type)
        )

    @classmethod
    def from_fort_details_proto(cls, proto: FortDetailsOutProto):
        return cls(
            id_=proto.id,
            lat=proto.latitude,
            lon=proto.longitude,
            type_=FortType.from_proto_type(proto.fort_type),
            name=proto.name if proto.name else None,
            description=proto.description if proto.description else None,
            cover_image=proto.image_url[0] if proto.image_url else None
        )

    @staticmethod
    def game_from_type(fort_type: FortType) -> Game:
        if fort_type.value >= 30:
            return Game.LIGHTSHIP
        if fort_type.value >= 20:
            return Game.INGRESS
        if fort_type.value >= 10:
            return Game.POGO
        return Game.UNKNOWN

    def add_other_fort(self, fort: Fort):
        for attr in ("name", "description", "cover_image"):
            if getattr(self, attr) is None and getattr(fort, attr) is not None:
                setattr(self, attr, getattr(fort, attr))
