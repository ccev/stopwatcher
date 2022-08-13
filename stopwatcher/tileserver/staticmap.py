from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TypeVar, TYPE_CHECKING

from stopwatcher.geo import Location

if TYPE_CHECKING:
    from stopwatcher.config import FortAppearancePartMapPart as FortAppearance


@dataclass
class _MapObject:
    pass


AnyMapObject = TypeVar("AnyMapObject", bound=_MapObject)


@dataclass
class Marker(_MapObject):
    location: Location
    url: str
    height: int = 32
    width: int = 32
    x_offset: int = 0
    y_offset: int = 0

    def __dict__(self):
        return {
            "url": self.url,
            "height": self.height,
            "width": self.width,
            "x_offset": self.x_offset,
            "y_offset": self.y_offset,
            "latitude": self.location.lat,
            "longitude": self.location.lon
        }


@dataclass
class Circle(_MapObject):
    location: Location
    fill_color: str
    stroke_width: int
    stroke_color: str
    radius: float

    def __dict__(self):
        return {
            "fill_color": self.fill_color,
            "stroke_color": self.stroke_color,
            "stroke_width": self.stroke_width,
            "radius": self.radius,
            "latitude": self.location.lat,
            "longitude": self.location.lon
        }


@dataclass
class Polygon(_MapObject):
    path: list[Location]
    fill_color: str
    stroke_width: int
    stroke_color: str

    def __dict__(self):
        return {
            "fill_color": self.fill_color,
            "stroke_color": self.stroke_color,
            "stroke_width": self.stroke_width,
            "path": [[loc.lat, loc.lon] for loc in self.path]
        }


@dataclass
class Bounds:
    min: Location
    max: Location


class StaticMap:
    def __init__(self, style: str, location: Location, zoom: float, width: int, height: int, scale: int):
        self.style: str = style
        self.location: Location = location
        self.zoom: float = zoom
        self.width: int = width
        self.height: int = height
        self.scale: int = scale

        self._markers: list[Marker] = []
        self._circles: list[Circle] = []
        self._polygons: list[Polygon] = []

    def __dict__(self):
        map_objects = {}
        for key, obj_list in (("markers", self._markers), ("circles", self._circles), ("polygons", self._polygons)):
            if obj_list:
                map_objects[key] = [m.__dict__() for m in obj_list]

        return {
            "style": self.style,
            "latitude": self.location.lat,
            "longitude": self.location.lon,
            "zoom": self.zoom,
            "width": self.width,
            "height": self.height,
            "scale": self.scale,
            "format": "png",
            **map_objects
        }

    def __point_to_lat(self, x: int, y: int) -> tuple[float, float]:
        c = (256 / (2 * math.pi)) * 2 ** self.zoom

        xcenter = c * (math.radians(self.location.lon) + math.pi)
        ycenter = c * (math.pi - math.log(math.tan((math.pi / 4) + math.radians(self.location.lat) / 2)))

        xpoint = xcenter - (self.width / 2 - x)
        ypoint = ycenter - (self.height / 2 - y)

        c = (256 / (2 * math.pi)) * 2 ** self.zoom
        m = (xpoint / c) - math.pi
        n = -(ypoint / c) + math.pi

        fin_lon = math.degrees(m)
        fin_lat = math.degrees((math.atan(math.e ** n) - (math.pi / 4)) * 2)

        return fin_lat, fin_lon

    def get_bounds(self) -> Bounds:
        lat_1, lon_1 = self.__point_to_lat(0, 0)
        lat_2, lon_2 = self.__point_to_lat(x=self.width, y=self.height)

        return Bounds(
            max=Location(lat=max(lat_1, lat_2), lon=max(lon_1, lon_2)),
            min=Location(lat=min(lat_1, lat_2), lon=min(lon_1, lon_2))
        )

    def add_marker(
        self, location: Location, url: str, height: int = 32, width: int = 32, x_offset: int = 0, y_offset: int = 0
    ):
        self._markers.append(
            Marker(location=location, url=url, height=height, width=width, x_offset=x_offset, y_offset=y_offset)
        )

    def add_fort(self, location: Location, fort_appear: FortAppearance):
        self.add_marker(
            location=location,
            url=fort_appear.icon,
            height=fort_appear.height,
            width=fort_appear.width,
            x_offset=fort_appear.x_offset,
            y_offset=fort_appear.y_offset
        )

    def add_circle(
        self,
        location: Location,
        fill_color: str,
        stroke_width: int,
        stroke_color: str,
        radius: float,
    ):
        self._circles.append(
            Circle(
                location=location,
                fill_color=fill_color,
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                radius=radius,
            )
        )

    def add_polygon(self, path: list[Location], fill_color: str, stroke_width: int, stroke_color: str):
        self._polygons.append(
            Polygon(path=path, fill_color=fill_color, stroke_width=stroke_width, stroke_color=stroke_color)
        )
