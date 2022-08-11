from abc import abstractmethod

from pypika import Table


class Base(Table):
    @property
    @abstractmethod
    def __table__(self) -> str:
        pass

    def __init__(self):
        super().__init__(self.__table__)
