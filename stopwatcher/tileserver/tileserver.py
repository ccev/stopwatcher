from __future__ import annotations
from typing import TYPE_CHECKING
from aiohttp import ClientSession
from stopwatcher.log import log

if TYPE_CHECKING:
    from .staticmap import StaticMap


class Tileserver:
    _session: ClientSession

    def __init__(self, url: str):
        self._url = url

    async def connect(self):
        if hasattr(self, "_session"):
            await self._session.close()

        self._session = ClientSession()

    async def pregenerate_staticmap(self, staticmap: StaticMap) -> str:
        if not hasattr(self, "_session"):
            await self.connect()

        first_url = self._url + "/staticmap?pregenerate=true&regeneratable=true"

        try:
            result = await self._session.post(first_url, json=staticmap.__dict__())
        except RuntimeError as e:
            log.error(f"Error while requesting staticmap {e}")
            await self.connect()
            return ""

        text = await result.text()

        if "error" in text:
            log.error(f"Error while pregenerating staticmap: {text}")
            return ""

        return self._url + f"/staticmap/pregenerated/{text}"
