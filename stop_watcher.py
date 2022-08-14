import asyncio
from asyncio import Queue

from aiohttp import web

from stopwatcher.accepter import DataAccepter
from stopwatcher.comparer import FortComparer
from stopwatcher.config import config
from stopwatcher.db.accessor import DbAccessor
from stopwatcher.job_worker import JobWorker
from stopwatcher.tileserver import Tileserver
from stopwatcher.watcher_jobs import SetQueue
from stopwatcher.external_db_reader import ExternalDbReader


async def main():
    processing_queue = Queue()
    job_queue = SetQueue()

    if config.tileserver.enable:
        tileserver = Tileserver(config.tileserver.url)
    else:
        tileserver = None

    db_accessor = DbAccessor()
    await db_accessor.connect(asyncio.get_running_loop())

    if config.data_input.database:
        ExternalDbReader(accessor=db_accessor, process_queue=processing_queue)

    if config.data_input.webhooks.enable:
        accepter = DataAccepter(process_queue=processing_queue)
        asyncio.create_task(
            web._run_app(
                app=accepter.app,
                host=config.data_input.webhooks.host,
                port=config.data_input.webhooks.port,
                access_log=None
            )
        )

    FortComparer(accessor=db_accessor, inbound_queue=processing_queue, outbound_queue=job_queue)
    JobWorker(queue=job_queue, tileserver=tileserver, accessor=db_accessor)

    await asyncio.Event().wait()


asyncio.run(main())
