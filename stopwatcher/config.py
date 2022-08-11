from __future__ import annotations

import sys

import rtoml
from pydantic import BaseModel, ValidationError

from .log import log


class DbConnection(BaseModel):
    username: str
    password: str
    host: str
    port: int
    database: str


class Webhooks(BaseModel):
    enable: bool
    host: str
    port: int
    username: str
    password: str


class DataInput(BaseModel):
    webhooks: Webhooks = Webhooks(enable=False, host="", port=0, username="", password="")


class DiscordWebhook(BaseModel):
    webhooks: list[str]
    types: list[str]
    send: list[str]


class Area(BaseModel):
    name: str
    discord: list[DiscordWebhook]


class Config(BaseModel):
    stopwatcher_db: DbConnection
    data_input: DataInput
    areas: list[Area]


with open("config.toml", mode="r") as config_file:
    raw_config = rtoml.load(config_file)


raw_areas = list(raw_config.get("areas").items())
raw_config["areas"] = []
for area_name, area_config in raw_areas:
    discord = area_config.pop("discord", {})
    raw_config["areas"].append({"name": area_name, "discord": list(discord.values()), **area_config})

try:
    config = Config(**raw_config)
except ValidationError as e:
    log.error(f"Config validation error!\n{e}")
    sys.exit(1)

config = config
