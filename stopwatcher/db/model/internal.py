from pypika import Field

from .base import Base


class FortTable(Base):
    __table__ = "sw_fort"

    id = Field("id")
    game_id = Field("game_id")
    type_id = Field("type_id")
    lat = Field("lat")
    lon = Field("lon")
    name = Field("name")
    description = Field("description")
    cover_image = Field("cover_image")


fort_table = FortTable()
