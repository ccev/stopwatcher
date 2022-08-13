from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from shapely.geometry import Polygon, Point


@dataclass
class Location:
    lat: float
    lon: float

    def __eq__(self, other: Location):
        return isclose(self.lat, other.lat) and isclose(self.lon, other.lon)


@dataclass
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
