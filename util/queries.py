from pymysql import connect

class create_queries():
    def __init__(self, config, cursor):
        self.cursor = cursor
        self.portal = config.db_name_portal
        self.extra = config.db_name_extra
        self.schema = config.scan_type
        self.geofences = config.geofences

    def convert_area(self, area_name):
        stringfence = "-100 -100, -100 100, 100 100, 100 -100, -100 -100"
        for area in self.geofences:
            if area['name'].lower() == area_name.lower():
                stringfence = ""
                for coordinates in area['path']:
                    stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
                stringfence = f"{stringfence}{area['path'][0][0]} {area['path'][0][1]}"
        self.area = stringfence

    def get_portals(self, area):
        self.convert_area(area)
        self.cursor.execute(f"SELECT id, lat, lon, name, url FROM {self.portal}.ingress_portals WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
        portals = self.cursor.fetchall()
        return portals

    def get_stops(self, area):
        self.convert_area(area)
        if self.schema == "mad":
            self.cursor.execute(f"SELECT pokestop_id, latitude, longitude, name, image FROM pokestop WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(latitude, longitude));")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id, lat, lon, name, url FROM pokestop WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
        stops = self.cursor.fetchall()
        return stops

    def get_gyms(self, area):
        self.convert_area(area)
        if self.schema == "mad":
            self.cursor.execute(f"SELECT gymdetails.gym_id, latitude, longitude, name, url FROM gym LEFT JOIN gymdetails on gym.gym_id = gymdetails.gym_id WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(latitude, longitude));")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id, lat, lon, name, url FROM gym WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
        gyms = self.cursor.fetchall()
        return gyms

    def get_empty_stops(self, area):
        return

    def get_empty_gyms(self, area):
        return

    def get_converted_stops(self, area):
        self.convert_area(area)
        if self.schema == "mad":
            self.cursor.execute(f"SELECT pokestop_id FROM pokestop WHERE pokestop_id IN (SELECT gym_id FROM gym) AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(latitude, longitude));")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id FROM pokestop WHERE (SELECT id FROM gym) AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
        stops = self.cursor.fetchall()
        return stops

    def delete_stop(self, s_id):
        if self.schema == "mad":
            self.cursor.execute(f"DELETE FROM pokestop WHERE pokestop_id = {s_id};")
        elif self.schema == "rdm":
            self.cursor.execute(f"DELETE FROM pokestop WHERE id = {s_id};")