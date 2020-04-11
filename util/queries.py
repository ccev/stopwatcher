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
        self.cursor.execute(f"SELECT external_id, lat, lon, name, url FROM {self.portal}.ingress_portals WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
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
        self.convert_area(area)
        if self.schema == "mad":
            self.cursor.execute(f"SELECT pokestop_id FROM pokestop WHERE name IS NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(latitude, longitude));")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id FROM pokestop WHERE name IS NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
        stops = self.cursor.fetchall()
        return stops

    def get_empty_gyms(self, area):
        self.convert_area(area)
        if self.schema == "mad":
            self.cursor.execute(f"SELECT gym.gym_id FROM gym LEFT JOIN gymdetails on gym.gym_id = gymdetails.gym_id WHERE name = 'unknown' AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(latitude, longitude));")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id FROM gym WHERE name IS NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
        gyms = self.cursor.fetchall()
        return gyms

    def get_converted_stops(self, area):
        self.convert_area(area)
        if self.schema == "mad":
            self.cursor.execute(f"SELECT pokestop_id, name FROM pokestop WHERE pokestop_id IN (SELECT gym_id FROM gym) AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(latitude, longitude));")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT id, name FROM pokestop WHERE (SELECT id FROM gym) AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({self.area}))'), point(lat, lon));")
        stops = self.cursor.fetchall()
        return stops

    def delete_stop(self, s_id):
        if self.schema == "mad":
            self.cursor.execute(f"DELETE FROM pokestop WHERE pokestop_id = '{s_id}';")
        elif self.schema == "rdm":
            self.cursor.execute(f"DELETE FROM pokestop WHERE id = '{s_id}';")

    def update_waypoint(self, w_type, w_id, w_name, w_img):
        if self.schema == "mad":
            if w_type == "stop":
                table = "pokestop"
                c_id = "pokestop_id"
                img = "image"
            elif w_type == "gym":
                table = "gymdetails"
                c_id = "gym_id"
                img = "url"
            self.cursor.execute(f"UPDATE {table} SET {img} = '{w_img}', name = '{w_name}' WHERE ({c_id} = '{w_id}');")
        elif self.schema == "rdm":
            if w_type == "stop":
                table = "pokestop"
            elif w_type == "gym":
                table = "gym"
            self.cursor.execute(f"UPDATE {table} SET url = '{w_img}', name = '{w_name}' WHERE (id = '{w_id}');")

    def get_stop_by_id(self, w_id):
        if self.schema == "mad":
            self.cursor.execute(f"SELECT name, image FROM pokestop WHERE pokestop_id = '{w_id}';")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT name, url FROM pokestop WHERE id = '{w_id}';")
        stops = self.cursor.fetchall()
        return stops

    def get_portal_by_id(self, w_id):
        self.cursor.execute(f"SELECT name, url FROM {self.portal}.ingress_portals WHERE external_id = '{w_id}';")
        portals = self.cursor.fetchall()
        return portals

    def get_full_portal_by_id(self, w_id):
        self.cursor.execute(f"SELECT lat, lon, name, url FROM {self.portal}.ingress_portals WHERE external_id = '{w_id}';")
        portal = self.cursor.fetchone()
        return portal
    
    def get_full_stop_by_id(self, w_id):
        if self.schema == "mad":
            self.cursor.execute(f"SELECT latitude, longitude name, image FROM pokestop WHERE pokestop_id = '{w_id}';")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT lat, lon, name, url FROM pokestop WHERE id = '{w_id}';")
        stops = self.cursor.fetchone()
        return stops

    def get_full_gym_by_id(self, w_id):
        self.convert_area(area)
        if self.schema == "mad":
            self.cursor.execute(f"SELECT latitude, longitude, name, url FROM gym LEFT JOIN gymdetails on gym.gym_id = gymdetails.gym_id WHERE gym.gym_id = {w_id};")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT lat, lon, name, url FROM gym WHERE id = {w_id};")
        gyms = self.cursor.fetchone()
        return gyms

    def create_edit_list(self, edit_list):
        try:
            portals = self.get_portals("")
            for p_id, p_lat, p_lon, p_name, p_img in portals:
                edit_list["portals"].append([p_id, p_lat, p_lon, p_name, p_img])
        except:
            edit_list["portals"] = []
        
        try:
            stops = self.get_portals("")
            for s_id, s_lat, s_lon, s_name, s_img in stops:
                edit_list["stops"].append([s_id, s_lat, s_lon, s_name, s_img])
        except:
            edit_list["stops"] = []
        
        try:
            gyms = self.get_gyms("")
            for g_id, g_lat, g_lon, g_name, g_img in gyms:
                edit_list["gyms"].append([g_id, g_lat, g_lon, g_name, g_img])
        except:
            edit_list["gyms"] = []
        
        return edit_list