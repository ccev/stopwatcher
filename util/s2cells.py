import s2sphere

# I copied most of this code from Map-A-Droid.

class s2cell():
    def __init__(self, queries, lat, lon, level):
        """regionCover = s2sphere.RegionCoverer()
        regionCover.min_level = level
        regionCover.max_level = level
        regionCover.max_cells = 1
        p1 = s2sphere.LatLng.from_degrees(lat, lon)
        p2 = s2sphere.LatLng.from_degrees(lat, lon)
        covering = regionCover.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
        cellId = covering[0].id()
        """
        ll = s2sphere.LatLng.from_degrees(lat, lon)
        cell = s2sphere.CellId().from_lat_lng(ll)
        cellId = cell.parent(level).id()
        cell = s2sphere.Cell(s2sphere.CellId(cellId))

        path = []
        for v in range(0, 4):
            vertex = s2sphere.LatLng.from_point(cell.get_vertex(v))
            path.append([vertex.lat().degrees, vertex.lng().degrees])

        mb_path = []
        for v in range(0, 4):
            vertex = s2sphere.LatLng.from_point(cell.get_vertex(v))
            mb_path.append([vertex.lng().degrees, vertex.lat().degrees])
        mb_path.append(mb_path[0])

        stringfence = ""
        for coordinates in path:
            stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
        stringfence = f"{stringfence}{path[0][0]} {path[0][1]}"
        count = queries.count_in_cell(stringfence)

        self.path = path
        self.mapbox_path = mb_path
        self.stops = count[0]
        self.gyms = count[1]


        