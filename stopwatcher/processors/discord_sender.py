from __future__ import annotations

from typing import TYPE_CHECKING, Type

import aiohttp
import discord

from stopwatcher.config import poi_appearance
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

if TYPE_CHECKING:
    from stopwatcher.config import DiscordWebhook as WebhookConfig
    from stopwatcher.watcher_jobs import AnyWatcherJob


class DiscordSender(BaseProcessor):
    def __init__(self, config: WebhookConfig, tileserver: Tileserver | None):
        self._config: WebhookConfig = config
        self._session = aiohttp.ClientSession()
        self._tileserver: Tileserver | None = tileserver

        self._webhooks: list[discord.Webhook] = [
            discord.Webhook.from_url(url=w, session=self._session) for w in self._config.webhooks
        ]

    async def _send_webhook(self, user: str, avatar: str, embeds: list[discord.Embed]):
        for webhook in self._webhooks:
            await webhook.send(embeds=embeds, username=user, avatar_url=avatar)

    async def process(self, job: AnyWatcherJob) -> None:
        if job.fort.type.name.lower() not in self._config.types:
            return

        def check(job_type: Type[AnyWatcherJob]) -> bool:
            return isinstance(job, job_type) and job.__key__ in self._config.send

        embed = discord.Embed()
        embeds = [embed]

        type_name = poi_appearance.names.get(job.fort.type)
        type_icon = poi_appearance.icons.get(job.fort.type)

        author: str = ""

        if check(NewFortJob):
            author = f"New {type_name}"
        elif check(NewFortDetailsJob):
            if NewFortJob.__key__ in self._config.send:
                author = f"{type_name} Details"
            else:
                author = f"New {type_name}"
        elif check(RemovedFortJob):
            author = "Removed"
        elif check(ChangedFortTypeJob):
            old_type_name = poi_appearance.names.get(job.old)
            author = f"{old_type_name} → {type_name}"
        elif check(ChangedNameJob):
            author = "New Name"
            embed.description = f"Old: `{job.old}`\nNew: `{job.new}`"
        elif check(ChangedDescriptionJob):
            author = "New Description"
            embed.description = f"Old: `{job.old}`\nNew: `{job.new}`"
        elif check(ChangedLocationJob):
            author = "New Location"
        elif check(ChangedCoverImageJob):
            author = "New Image"
            image_embed = discord.Embed()
            image_embed.set_image(url=job.fort.cover_image)
            embeds.append(image_embed)

        if author:
            if self._tileserver is not None:
                staticmap = StaticMap(
                    style="osm-bright", location=job.fort.location, zoom=17.5, width=800, height=500, scale=1
                )
                staticmap.add_marker(location=job.fort.location, url=type_icon)
                map_url = await self._tileserver.pregenerate_staticmap(staticmap)
                embed.set_image(url=map_url)

            if job.fort.name is not None:
                embed.title = job.fort.name
            if job.fort.cover_image is not None:
                embed.set_thumbnail(url=job.fort.cover_image)
            if job.fort.description is not None:
                extra_text = f"*{job.fort.description}*"
                if embed.description:
                    embed.description = f"{extra_text}\n\n{embed.description}"
                else:
                    embed.description = extra_text

            # embed.set_author(name=author)
            await self._send_webhook(user=author, avatar=type_icon, embeds=embeds)

