from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from stopwatcher.watcher_jobs import AnyWatcherJob


class BaseProcessor(metaclass=ABCMeta):
    @abstractmethod
    async def process(self, job: AnyWatcherJob) -> None:
        pass


AnyProcessor = TypeVar("AnyProcessor", bound=BaseProcessor)
