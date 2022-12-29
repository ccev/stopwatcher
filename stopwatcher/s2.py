import s2sphere

from .geo import Location, Geofence


def get_cell_id_from_location(location: Location, level: int = 15) -> s2sphere.CellId:
    coords = s2sphere.LatLng.from_degrees(lat=location.lat, lng=location.lon)
    base_cell = s2sphere.CellId.from_lat_lng(coords)
    return base_cell.parent(level)


def get_cell_vertices(location: Location) -> list[Location]:
    cell_id = get_cell_id_from_location(location, level=17)
    cell = s2sphere.Cell(cell_id)
    path: list[Location] = []

    for v in range(4):
        vertex = s2sphere.LatLng.from_point(cell.get_vertex(v))
        path.append(Location(vertex.lat().degrees, vertex.lng().degrees))
    return path


class Cell:
    def __init__(self, cell_id: s2sphere.CellId):
        self.cell: s2sphere.Cell = s2sphere.Cell(cell_id)

        path = []
        for v in range(4):
            vertex = s2sphere.LatLng.from_point(self.cell.get_vertex(v))
            path.append((vertex.lat().degrees, vertex.lng().degrees))

        self.fence: Geofence = Geofence(path)

    @classmethod
    def from_cell_id(cls, cell_id: int):
        return cls(s2sphere.CellId(cell_id))

    @classmethod
    def from_location(cls, location: Location, level: int = 15):
        return cls(get_cell_id_from_location(location, level))

    def contains(self, location: Location) -> bool:
        return self.fence.contains(location)
