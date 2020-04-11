import requests
import time
import json

class waypoint():
    def __init__(self, queries, config, wf_type, wf_id, name = None, img = None, lat = None, lon = None):
        self.queries = queries
        self.config = config
        self.locale = config.locale
        self.id = wf_id
        self.type = wf_type
        self.name = name
        self.img = img
        self.lat = lat
        self.lon = lon
        self.edit = False

        self.empty = False
        if self.name is None or self.name == "unknown":
            self.empty = True

    def update(self):
        needs_update = True
        if self.type == "gym":
            try:
                stop = self.queries.get_stop_by_id(self.id)
                for s_name, s_img in stop:
                    if s_name is not None:
                        self.queries.update_waypoint(self.type, self.id, s_name, s_img)
                        print(f"Updated {self.type} {s_name}")
                        needs_update = False
            except:
                needs_update = True

        if needs_update:
            try:
                portal = self.queries.get_portal_by_id(self.id)
                for p_name, p_img in portal:
                    if p_name is not None:
                        self.queries.update_waypoint(self.type, self.id, p_name, p_img)
                        print(f"Updated {self.type} {p_name}")
                        needs_update = False
            except:
                needs_update = True

    def delete(self):
        print(f"Deleting converted {self.type} {self.name} from your DB")
        self.queries.delete_stop(self.id)

    def send(self, fil, text = "", title = ""):     
        # Title + image
        image = self.img
        if not self.edit:
            print(f"Found {self.type} {self.name} - Sending now")
            title = self.name
        if self.empty:
            title = ""
            image = ""

        # Text
        links = f"[Google Maps](https://www.google.com/maps/search/?api=1&query={self.lat},{self.lon})"
        if self.type == "portal":
            links = f"{links} | [Intel](https://intel.ingress.com/intel?ll={self.lat},{self.lon}&z=18&pll={self.lat},{self.lon})"

        if self.config.use_map:
            map_url = ""
            if self.config.map_provider == "pmsf":
                map_url = f"{self.config.map_url}?lat={self.lat}&lon={self.lon}&zoom=18"
                if self.type == "stop":
                    map_url = f"{map_url}&stopId={self.id}"
                elif self.type == "gym":
                    map_url = f"{map_url}&gymId={self.id}"
            elif self.config.map_provider == "rdm":
                if self.type == "portal":
                    map_url = f"{self.config.map_url}@/{self.lat}/{self.lon}/18"
                elif self.type == "stop":
                    map_url = f"{self.config.map_url}@pokestop/:{self.id}"
                elif self.type == "gym":
                    map_url = f"{self.config.map_url}@gym/:{self.id}"
            elif self.config.map_provider == "rmad":
                map_url = f"{self.config.map_url}?lat={self.lat}&lon={self.lon}&zoom=18"
            links = f"{links} \\| [{self.config.map_name}]({map_url})"

        # WP specific stuff
        if self.type == "portal":
            static_color = "c067fc"
            embed_color = 12609532
            embed_username = self.locale["portal_name"]
            embed_avatar = "https://raw.githubusercontent.com/ccev/stopwatcher/master/icons/portal.png"
            if self.edit:
                embed_username = self.locale["portal_edit_name"]
        elif self.type == "stop":
            static_color = "128fed"
            embed_color = 1216493
            embed_username = self.locale["stop_name"]
            embed_avatar = "https://raw.githubusercontent.com/ccev/stopwatcher/master/icons/stop.png"
            if self.edit:
                embed_username = self.locale["stop_edit_name"]
        elif self.type == "gym":
            static_color = "bac0c5"
            embed_color = 12239045
            embed_username = self.locale["gym_name"]
            embed_avatar = "https://raw.githubusercontent.com/ccev/stopwatcher/master/icons/gym.png"
            if self.edit:
                embed_username = self.locale["gym_edit_name"]

        # Static Map
        static_map = ""
        if self.config.static_provider == "google":
            static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={self.lat},{self.lon}&zoom=18&scale=1&size=800x500&maptype=roadmap&key={self.config.static_key}&format=png&visual_refresh=true&markers=size:normal%7Ccolor:0x{static_color}%7Clabel:%7C{self.lat},{self.lon}"
        elif self.config.static_provider == "osm":
            static_map = f"https://www.mapquestapi.com/staticmap/v5/map?locations={self.lat},{self.lon}&size=800,500&defaultMarker=marker-md-{static_color}&zoom=18&key={self.config.static_key}"
        elif self.config.static_provider == "tileserver-gl":
            static_map = (config['static_selfhosted_url'] + "static/klokantech-basic/" + str(lat) + "/" + str(lon) + "/" + str(config['static_zoom']) + "/" + str(config['static_width']) + "/" + str(config['static_height']) + "/1/png?markers=%5B%7B%22url%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png%22%2C%22height%22%3A128%2C%22width%22%3A128%2C%22x_offset%22%3A0%2C%22y_offset%22%3A0%2C%22latitude%22%3A%20" + str(lat) + "%2C%22longitude%22%3A%20" + str(lon) + "%7D%5D")    
        elif self.config.static_provider == "mapbox":
            return

        # Send
        if "webhook" in fil:
            data = {
                "username": embed_username,
                "avatar_url": embed_avatar,
                "embeds": [{
                    "title": title,
                    "description": f"{text}\n\n{links}",
                    "color": embed_color,
                    "thumbnail": {
                        "url": image
                    },
                    "image": {
                        "url": static_map
                    }
                }]
            }
            for webhook in fil["webhook"]:
                result = requests.post(webhook, json=data)
                print(result)
                time.sleep(2)

        if "bot_id" in fil:
            for chat_id in fil["chat_id"]:
                if not self.empty:
                    payload = {"chat_id": str(chat_id), "photo": image}
                    result = requests.get(f"https://api.telegram.org/bot{fil['bot_id']}/sendPhoto", params = payload)
                    print(f"Result {result.status_code} for Photo")
                if not text == "":
                    text = f"\n{text}"
                payload = {"chat_id": str(chat_id), "parse_mode": "markdownv2", "text": f"*{embed_username}*\n{title}{text}\n\n[‌‌]({static_map}){links}"}
                result = requests.get(f"https://api.telegram.org/bot{fil['bot_id']}/sendMessage", params = payload)
                print(f"Result {result.status_code} for Text")
                time.sleep(2)

    def send_location_edit(self, fil, old_lat, old_lon):
        print(f"Found edited location of {self.type} {self.name} - Sending now.")
        self.edit = True
        title = self.locale["location_edit_title"].format(name = self.name)
        text = self.locale["edit_text"].format(old = f"`{old_lat},{old_lon}`", new = f"`{self.lat},{self.lon}`")
        self.send(fil, text, title)

    def send_name_edit(self, fil, old_name):
        print(f"Found edited name of {self.type} {old_name} - Sending now.")
        self.edit = True
        title = self.locale["name_edit_title"].format(name = self.name)
        text = self.locale["edit_text"].format(old = f"`{old_name}`", new = f"`{self.name}`")
        self.send(fil, text, title)

    def send_img_edit(self, fil, old_img):
        print(f"Found new image for {self.type} {self.name} - Sending now.")
        self.edit = True
        title = self.locale["img_edit_title"].format(name = self.name)
        text = self.locale["edit_text"].format(old = f"[Link]({old_img})", new = f"`[Link]({self.img})")
        self.send(fil, text, title)

    def send_deleted(self, fil):
        print(f"Found possibly removed {self.type} {self.name} :o")
        self.edit = True
        title = self.locale["deleted_title"].format(name = self.name)
        self.send(fil, "", title)

class init():
    def __init__(self, queries):
        self.queries = queries
    
    def write_portals(self, portal_cache):
        portals = self.queries.get_portals("")
        for p_id, p_lat, p_lon, p_name, p_img in portals:
            if not p_id in portal_cache:
                portal_cache.append(p_id)
        return portal_cache

    def write_stops(self, stop_cache):
        stops = self.queries.get_stops("")
        for s_id, s_lat, s_lon, s_name, s_img in stops:
            if not s_id in stop_cache:
                stop_cache.append(s_id)
        return stop_cache

    def write_gyms(self, gym_cache):
        gyms = self.queries.get_gyms("")
        for g_id, g_lat, g_lon, g_name, g_img in gyms:
            if not g_id in gym_cache:
                gym_cache.append(g_id)
        return gym_cache