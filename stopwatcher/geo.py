from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from shapely.geometry import Polygon, Point


def _middle(one: float, two: float) -> float:
    return min(one, two) + (max(one, two) - min(one, two)) / 2


@dataclass
class Location:
    lat: float
    lon: float

    def __eq__(self, other: Location):
        return isclose(self.lat, other.lat) and isclose(self.lon, other.lon)

    @classmethod
    def middle(cls, loc_1: Location, loc_2: Location):
        return cls(lat=_middle(loc_1.lat, loc_2.lat), lon=_middle(loc_1.lon, loc_2.lon))


class Geofence:
    def __init__(self, raw_fence: str):
        bounds = []
        for line in raw_fence.splitlines():
            try:
                lat, lon = line.split(",")
                lat, lon = float(lat), float(lon)
            except ValueError:
                continue

            bounds.append((lat, lon))

        self.polygon = Polygon(bounds)

    def contains(self, location: Location) -> bool:
        return self.polygon.contains(Point(location.lat, location.lon))
