import s2sphere

class s2cell():
    def __init__(self, queries, lat, lon, level):
        """
        I copied most of this code from Map-A-Droid.
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
        self.stops = count[0] + count[1]

    def converts(self):
        if self.stops == 0:
            return True
        else:
            return False

    def brings_gym(self):
        if (self.stops == 1) or (self.stops == 5) or (self.stops == 19):
            return True
        else:
            return False

    def next_threshold(self):
        total = 20
        for i in [1, 5, 19]:
            if self.stops <= i:
                total = i + 1
                return total