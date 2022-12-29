from __future__ import annotations

from typing import TYPE_CHECKING, Type
from io import BytesIO

import aiohttp
import discord
import asyncio
from PIL import Image, ImageDraw

from stopwatcher.config import poi_appearance, config
from stopwatcher.tileserver import Tileserver, StaticMap
from stopwatcher.watcher_jobs import (
    NewFortJob,
    RemovedFortJob,
    ChangedFortTypeJob,
    ChangedNameJob,
    ChangedDescriptionJob,
    ChangedLocationJob,
    ChangedCoverImageJob,
    NewFortDetailsJob,
)
from .base_processor import BaseProcessor
from stopwatcher.db.helper.internal_fort import FortHelper
from stopwatcher.geo import Location
from stopwatcher.log import log

if TYPE_CHECKING:
    from stopwatcher.config import DiscordWebhook as WebhookConfig
    from stopwatcher.watcher_jobs import AnyWatcherJob
    from stopwatcher.db.accessor import DbAccessor


class DiscordSender(BaseProcessor):
    def __init__(self, wh_config: WebhookConfig, tileserver: Tileserver | None, accessor: DbAccessor):
        self._config: WebhookConfig = wh_config
        self._session = aiohttp.ClientSession()
        self._tileserver: Tileserver | None = tileserver
        self._db_accessor: DbAccessor = accessor

        self._webhooks: list[discord.Webhook] = [
            discord.Webhook.from_url(url=w, session=self._session) for w in self._config.webhooks
        ]

    @staticmethod
    async def __download_image(url: str) -> Image.Image:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.read()

        with BytesIO(result) as stream:
            image = Image.open(stream).copy()
            image = image.convert("RGBA")
        return image

    @staticmethod
    def __make_cover_change_image_(old: Image.Image, new: Image.Image) -> Image.Image:
        old_width, old_height = old.size
        new_width, new_height = new.size
        border_width = (old_width + new_width) // 30
        bg_height = max(old_height, new_height)

        background = Image.new(
            "RGBA", (old_width + new_width + border_width, bg_height), (255, 0, 0, 0)
        )
        background.paste(old, (0, (bg_height - old_height) // 2))
        background.paste(new, (old_width + border_width, (bg_height - new_height) // 2))

        return background

    async def _send_webhook(self, user: str, avatar: str, embeds: list[discord.Embed], **kwargs):
        for webhook in self._webhooks:
            await webhook.send(embeds=embeds, username=user, avatar_url=avatar, **kwargs)

    async def process(self, job: AnyWatcherJob) -> None:
        if job.fort.type.name.lower() not in self._config.types:
            return

        def check(job_type: Type[AnyWatcherJob]) -> bool:
            return isinstance(job, job_type) and job.__key__ in self._config.send

        appear = poi_appearance.get(job.fort.type)
        author: str = ""
        webhook_kwargs = {}

        embed = discord.Embed(color=appear.color)
        embeds = [embed]

        visual = config.tileserver.visual
        staticmap = StaticMap(
            style=visual.style,
            location=job.fort.location,
            zoom=visual.zoom,
            width=visual.width,
            height=visual.height,
            scale=visual.scale,
        )

        if check(NewFortJob):
            author = f"New {appear.name}"
        elif check(NewFortDetailsJob):
            if NewFortJob.__key__ in self._config.send:
                author = f"{appear.name} Details"
            else:
                author = f"New {appear.name}"
        elif check(RemovedFortJob):
            author = f"{appear.name} Removed"
        elif check(ChangedFortTypeJob):
            old_appear = poi_appearance.get(job.old)
            author = f"{old_appear.name} → {appear.name}"
        elif check(ChangedNameJob):
            author = f"New {appear.name} Name"
            embed.description = f"Old: **`{job.old}`**\nNew: **`{job.new}`**"
        elif check(ChangedDescriptionJob):
            author = f"New {appear.name} Description"

            def _get_formatted_text(raw: str | None) -> str:
                if not raw:
                    return "[No description]"
                return "> " + "\n> ".join(raw.split("\n"))

            embed.add_field(name="Old", value=_get_formatted_text(job.old), inline=False)
            embed.add_field(name="New", value=_get_formatted_text(job.new), inline=False)

        elif check(ChangedLocationJob):
            job: ChangedLocationJob
            author = f"New {appear.name} Location"

            if self._tileserver is not None:
                staticmap.location = Location.middle(job.old, job.new)
                staticmap.add_fort(location=job.old, fort_appear=appear.map.secondary)
                staticmap.add_fort(location=job.new, fort_appear=appear.map.primary)
                staticmap.auto_zoom()

        elif check(ChangedCoverImageJob):
            author = f"New {appear.name} Image"

            old_cover = await self.__download_image(job.old)
            new_cover = await self.__download_image(job.new)

            loop = asyncio.get_running_loop()
            extra_image = await loop.run_in_executor(None, self.__make_cover_change_image_, old_cover, new_cover)

            name = "changed_cover.png"
            with BytesIO() as image_binary:
                extra_image.save(image_binary, "PNG")
                image_binary.seek(0)
                file = discord.File(fp=image_binary, filename=name)
            image_embed = discord.Embed(color=appear.color)
            image_embed.set_image(url=f"attachment://{name}")
            embeds.append(image_embed)
            webhook_kwargs["file"] = file

        if author:
            log.info(f"Sending Discord notification for {job}")
            if self._tileserver is not None:
                if not isinstance(job, ChangedLocationJob):
                    if job.fort.type.name.lower() in config.tileserver.visual.nearby_forts:
                        bounds = staticmap.get_bounds()
                        sec_forts = await FortHelper.get_forts_in_bounds(
                            self._db_accessor, bounds=bounds, game=job.fort.game
                        )

                        for sec_fort in sec_forts:
                            if sec_fort.id == job.fort.id:
                                continue

                            sec_appear = poi_appearance.get(sec_fort.type)
                            staticmap.add_fort(location=sec_fort.location, fort_appear=sec_appear.map.secondary)

                    staticmap.add_fort(location=job.fort.location, fort_appear=appear.map.primary)

                map_url = await self._tileserver.pregenerate_staticmap(staticmap)
                embed.set_image(url=map_url)

            if job.fort.name is not None:
                embed.title = job.fort.name
            if job.fort.cover_image is not None:
                embed.set_thumbnail(url=job.fort.cover_image)
            if job.fort.description:
                extra_text = f"*{job.fort.description}*"
                if embed.description:
                    embed.description = f"{extra_text}\n\n{embed.description}"
                else:
                    embed.description = extra_text

            # embed.set_author(name=author)
            await self._send_webhook(user=author, avatar=appear.icon, embeds=embeds, **webhook_kwargs)
