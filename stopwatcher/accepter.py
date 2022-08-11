from __future__ import annotations

from asyncio import Queue

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_basicauth_middleware import basic_auth_middleware
from pydantic import BaseModel, ValidationError

from .fort import FortType, Fort
from .log import log


class FortRequest(BaseModel):
    id: str
    type: str
    lat: float
    lon: float
    name: str | None = None
    description: str | None = None
    cover_image: str | None = None


class DataAccepter:
    def __init__(self, process_queue: Queue, username: str, password: str):
        self.app = web.Application(logger=log)
        self.queue: Queue = process_queue

        routes = []
        for route, method in [("forts", self.accept_webhooks)]:
            routes.append(web.post(f"/{route}", method))
        self.app.add_routes(routes)

        self.app.middlewares.append(basic_auth_middleware(urls=("/",), auth_dict={username: password}))  # type: ignore

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
