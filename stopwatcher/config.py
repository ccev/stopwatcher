from __future__ import annotations

from typing import Type, TypeVar
import sys
import os

import rtoml
from pydantic import BaseModel, ValidationError

from .log import log
from .fort import FortType
from .geo import Geofence, Location


T = TypeVar("T")


class DbConnection(BaseModel):
    username: str
    password: str
    host: str
    port: int
    database: str


class DataInput(BaseModel):
    host: str
    port: int
    username: str
    password: str


class DiscordWebhook(BaseModel):
    webhooks: list[str]
    types: list[str]
    send: list[str]


class Area(BaseModel):
    name: str
    discord: list[DiscordWebhook]
    geofence: Geofence | None = None


class _VisualModelWithSize(BaseModel):
    size: str

    @property
    def width(self) -> int:
        return int(self.size.split("x")[0])

    @property
    def height(self) -> int:
        return int(self.size.split("x")[1])


class TileserverVisual(_VisualModelWithSize):
    style: str
    cells: list[str]
    nearby_forts: list[str]
    zoom: float
    scale: int


class Tileserver(BaseModel):
    enable: bool
    url: str
    visual: TileserverVisual


class General(BaseModel):
    geofence_path: str
    init: bool


class Config(BaseModel):
    general: General
    stopwatcher_db: DbConnection
    tileserver: Tileserver
    data_input: DataInput
    areas: list[Area]


class FortAppearancePartMapPart(_VisualModelWithSize):
    icon: str
    y_offset: int
    x_offset: int


class FortAppearancePartMap(BaseModel):
    primary: FortAppearancePartMapPart
    secondary: FortAppearancePartMapPart


class FortAppearancePart(BaseModel):
    name: str
    icon: str
    color: int
    map: FortAppearancePartMap


class FortAppearance(BaseModel):
    pokestop: FortAppearancePart
    gym: FortAppearancePart
    portal: FortAppearancePart
    lightship_poi: FortAppearancePart

    def get(self, fort_type: FortType) -> FortAppearancePart:
        return getattr(self, fort_type.name.lower())


def _get_raw_config(_config_file_name: str):
    config_path = os.path.join("config", _config_file_name)
    with open(config_path, mode="r") as _config_file:
        raw_config = rtoml.load(_config_file)
    return raw_config


def _load_pyd_model(model: Type[T], raw: dict) -> T:
    try:
        constructed_model = model(**raw)
    except ValidationError as e:
        log.error(f"Config validation error!\n{e}")
        sys.exit(1)

    return constructed_model


_raw_config = _get_raw_config("config.toml")
_raw_areas = list(_raw_config.get("areas").items())
_raw_config["areas"] = []
for area_name, area_config in _raw_areas:
    _discord = area_config.pop("discord", {})
    _raw_config["areas"].append({"name": area_name, "discord": list(_discord.values()), **area_config})

config: Config = _load_pyd_model(model=Config, raw=_raw_config)
poi_appearance: FortAppearance = _load_pyd_model(model=FortAppearance, raw=_get_raw_config("visual.toml"))


_geofences: dict[str, Geofence] = {}
for file in os.listdir(config.general.geofence_path):
    if not file.endswith(".txt"):
        continue

    with open(os.path.join(config.general.geofence_path, file), mode="r") as fence_file:
        _raw_fence = fence_file.read()

    if _raw_fence.startswith("[") and "]" in _raw_fence:
        _fence_name = _raw_fence.split("[", 1)[1].split("]")[0]
    else:
        _fence_name = file[:-4]

    _geofences[_fence_name] = Geofence(_raw_fence)

for _area in config.areas:
    _area.geofence = _geofences.get(_area.name)
