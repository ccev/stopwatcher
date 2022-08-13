from __future__ import annotations

from asyncio import Queue
import base64

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_basicauth_middleware import basic_auth_middleware
from pydantic import BaseModel, ValidationError
from protos import (
    Method,
    GetMapObjectsOutProto,
    FortDetailsOutProto,
    GymGetInfoOutProto,
    ClientMapCellProto,
    PokemonFortProto,
)

from .fort import FortType, Fort
from .log import log
from .config import config


class FortRequest(BaseModel):
    id: str
    type: str
    lat: float
    lon: float
    name: str | None = None
    description: str | None = None
    cover_image: str | None = None


class DataAccepter:
    def __init__(self, process_queue: Queue):
        self.app = web.Application(logger=log)
        self.queue: Queue = process_queue

        routes = [web.post("/forts", self.accept_webhooks), web.post("/protos", self.accept_protos)]
        self.app.middlewares.append(
            basic_auth_middleware(  # type: ignore
                urls=("/forts",), auth_dict={config.data_input.username: config.data_input.password}
            )
        )

        self.app.add_routes(routes)

        self._proto_map = {
            Method.METHOD_GET_MAP_OBJECTS: GetMapObjectsOutProto,
            Method.METHOD_GYM_GET_INFO: GymGetInfoOutProto,
            Method.METHOD_FORT_DETAILS: FortDetailsOutProto,
        }

    async def accept_protos(self, request: Request):
        log.debug(f"Received message from {request.remote}")

        if not request.can_read_body:
            log.warning(f"Couldn't read body of incoming request")
            return web.Response(status=400)

        data = await request.json()
        forts = []

        for raw_proto in data.get("contents", []):
            method_id: int = raw_proto.get("type", 0)

            message = self._proto_map.get(method_id)
            if message is None:
                continue

            payload = raw_proto.get("payload")

            if not payload:
                log.warning(f"Empty paylod in {raw_proto}")
                continue

            try:
                decoded = base64.b64decode(payload)
            except Exception as e:
                log.warning(f"Couldn't decode {payload} in {raw_proto}")
                continue

            try:
                proto = message()
                proto.ParseFromString(decoded)
            except Exception as e:
                log.exception(f"Unknown error while parsing proto {raw_proto}", e)
                continue

            if isinstance(proto, GetMapObjectsOutProto):
                for cell in proto.map_cell:
                    cell: ClientMapCellProto
                    for fort in cell.fort:
                        fort: PokemonFortProto
                        # forts.append(Fort.from_fort_proto(fort))

            elif isinstance(proto, FortDetailsOutProto):
                forts.append(Fort.from_fort_details_proto(proto))

        if forts:
            self.queue.put_nowait(forts)

        return web.Response()

    async def accept_webhooks(self, request: Request):
        log.debug(f"Received message from {request.remote}")

        if not request.can_read_body:
            log.warning(f"Couldn't read body of incoming request")
            return web.Response(status=400)

        data = await request.json()
        forts = []

        for raw_fort in data:

            try:
                parsed_fort = FortRequest(**raw_fort)
            except ValidationError as e:
                log.error(str(e))
                continue

            try:
                fort_type = FortType[parsed_fort.type.upper()]
            except KeyError:
                log.error(f"Unknown fort type <{parsed_fort.type}> in {raw_fort}")
                continue

            fort = Fort.from_request(request=parsed_fort, fort_type=fort_type)
            forts.append(fort)

        self.queue.put_nowait(forts)
        return web.Response()
