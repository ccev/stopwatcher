from __future__ import annotations

from dataclasses import dataclass
from math import isclose


@dataclass
class Location:
    lat: float
    lon: float

    def __eq__(self, other: Location):
        return isclose(self.lat, other.lat) and isclose(self.lon, other.lon)
