import asyncio
from asyncio import Queue

from aiohttp import web

from stopwatcher.accepter import DataAccepter
from stopwatcher.comparer import FortComparer
from stopwatcher.config import config
from stopwatcher.db.accessor import DbAccessor
from stopwatcher.job_worker import JobWorker
from stopwatcher.tileserver import Tileserver


async def main():
    processing_queue = Queue()
    job_queue = Queue()

    if config.tileserver.enable:
        tileserver = Tileserver(config.tileserver.url)
    else:
        tileserver = None

    wh_config = config.data_input.webhooks
    if wh_config.enable:
        accepter = DataAccepter(
            process_queue=processing_queue, username=wh_config.username, password=wh_config.password
        )

        asyncio.create_task(
            web._run_app(
                app=accepter.app,
                host=wh_config.host,
                port=wh_config.port,
            )
        )

    db_accessor = DbAccessor()
    await db_accessor.connect(asyncio.get_running_loop())

    FortComparer(accessor=db_accessor, inbound_queue=processing_queue, outbound_queue=job_queue)
    JobWorker(queue=job_queue, tileserver=tileserver, accessor=db_accessor)

    await asyncio.Event().wait()


asyncio.run(main())
