import requests
import time
import json

from datetime import datetime, timedelta

import util.static_map as StaticMap
from util.s2cells import s2cell

class waypoint():
    def __init__(self, queries, config, wf_type, wf_id, name = None, img = None, lat = 0, lon = 0):
        self.queries = queries
        self.config = config
        self.locale = config.locale
        self.id = wf_id
        self.type = wf_type
        self.name = name
        self.img = img
        self.lat = float(lat)
        self.lon = float(lon)
        self.edit = False
        self.edit_type = ""
        self.before_edit = None

        self.empty = False
        if self.name is None or self.name == "unknown":
            self.empty = True

    def update(self, stop_update = True):
        needs_update = True
        if self.type == "gym" and stop_update:
            try:
                stop = self.queries.get_full_stop_by_id(self.id)
                if stop[2] is not None:
                    self.queries.update_waypoint(self.type, self.id, stop[2], stop[3], stop[0], stop[1])
                    print(f"Updated {self.type} {stop[2]} using Stop info")
                    needs_update = False  
            except:
                needs_update = True

        if needs_update:
            try:
                portal = self.queries.get_full_portal_by_id(self.id)
                if portal[2] is not None:
                    self.queries.update_waypoint(self.type, self.id, portal[2], portal[3], portal[0], portal[1])
                    print(f"Updated {self.type} {portal[2]} using Portal info")
                    needs_update = False  
            except:
                needs_update = True

    def delete(self):
        print(f"Deleting converted {self.type} {self.name} from your DB")
        self.queries.delete_stop(self.id)

    def is_gym(self):
        if len(self.queries.get_gym_by_id(self.id)) == 0:
            return False
        else:
            return True

    def is_stop(self):
        if len(self.queries.get_stop_by_id(self.id)) == 0:
            return False
        else:
            return True

    def set_type(self, new_type):
        self.type = new_type

    def get_convert_time(self):
        utcnow = int(datetime.utcnow().strftime("%H"))
        now = int(datetime.now().strftime("%H"))
        offset = now - utcnow

        day = self.locale["today"]
        if utcnow >= 9:
            day = self.locale["tomorrow"]

        conv_time = (datetime(2020, 1, 1, 18, 0, 0) + timedelta(hours = offset)).strftime(self.locale["time_format"])
        convert_time = (self.locale['when_convert']).format(day = day, time = conv_time)
        return convert_time

    def send(self, fil, text = "", title = ""):     
        # Title + image
        image = self.img
        if not self.edit:
            print(f"Found {self.type} {self.name} - Sending now")
            title = self.name
        if self.empty:
            title = ""
            image = ""
        for char in ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
            title = title.replace(char, f"\\{char}")

        # Text
        convert_time = ""
        try:
            if self.type == "portal":
                if self.is_stop() or self.is_gym():
                    didnt_exist = False
                    convert_time = self.get_convert_time()
                else:
                    didnt_exist = True
                    
                stop_cell = s2cell(self.queries, self.lat, self.lon, 17)

                if not self.edit:
                    gym_cell = s2cell(self.queries, self.lat, self.lon, 14)

                    if stop_cell.converts():
                        text = self.locale["will_convert"]
                        convert_time = self.get_convert_time()
                    else:
                        text = self.locale["wont_convert"]

                    if self.is_stop():
                        text = self.locale["already_stop"]
                    elif self.is_gym():
                        text = self.locale["already_gym"]

                    if stop_cell.converts() and gym_cell.brings_gym():
                        text = f"{text}\n{self.locale['brings_gym']}"
                    else:
                        text = f"{text}\n{self.locale['brings_no_gym']}"

                    show_gym_stops = False
                    if stop_cell.converts():
                        gym_stops = gym_cell.stops + 1
                        show_gym_stops = True
                    elif self.is_gym() or self.is_stop():
                        convert_time = ""
                        gym_stops = gym_cell.stops
                        show_gym_stops = True

                    if show_gym_stops:
                        if gym_cell.stops > 20:
                            text = (f"{text}\n{self.locale['x_stop_in_cell_20']}").format(x = gym_stops)
                        else:
                            text = (f"{text}\n{self.locale['x_stop_in_cell']}").format(x = gym_stops, total = gym_cell.next_threshold())

                elif self.edit_type == "location":
                    text = f"{text}\n\n"
                    old_stop_cell = s2cell(self.queries, self.before_edit[0], self.before_edit[1], 17)

                    if old_stop_cell.path == stop_cell.path:
                        text = f"**{text}{self.locale['same_cell']}**:\n"
                        if not didnt_exist:
                            text = f"{text}{self.locale['stays_stop']}"
                        else:
                            text = f"{text}{self.locale['stays_no_stop']}"
                    
                    else:
                        text = f"{text}**{self.locale['new_cell']}**:\n"
                        if didnt_exist:
                            if stop_cell.converts():
                                text = f"{text}{self.locale['will_convert']}"
                            else:
                                text = f"{text}{self.locale['stays_no_stop']}"
                                convert_time = ""
                        else:
                            text = f"{text}{self.locale['stays_stop']}"

                        text = f"{text}\n**{self.locale['old_cell']}**:\n"
                        if old_stop_cell.portals == 0:
                            text = f"{text}{self.locale['cell_becomes_empty']}"
                        else:
                            if didnt_exist:
                                text = f"{text}{self.locale['cell_stays_occupied']}"
                            else:
                                text = f"{text}{self.locale['gets_new_stop']}"

                elif self.edit_type == "img":
                    convert_time = ""
                    
        except:
            pass

        links = f"[Google Maps](https://www.google.com/maps/search/?api=1&query={self.lat},{self.lon})"
        if self.type == "portal":
            links = f"{links} \\| [Intel](https://intel.ingress.com/intel?ll={self.lat},{self.lon}&z=18&pll={self.lat},{self.lon})"

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
                    map_url = f"{self.config.map_url}@pokestop/{self.id}"
                elif self.type == "gym":
                    map_url = f"{self.config.map_url}@gym/{self.id}"
            elif self.config.map_provider == "rmad":
                map_url = f"{self.config.map_url}?lat={self.lat}&lon={self.lon}&zoom=18"
            links = f"{links} \\| [{self.config.map_name}]({map_url})"
        
        address = ""
        if self.config.use_geocoding:
            geocode_template = {
                "provider": self.config.geocoding_provider,
                "key": self.config.geocoding_key,
                "text": "{address}"
            }
            new_geocode_template = {}
            for t in self.config.templates["geocoding"]:
                if self.type in t["for"]:
                    new_geocode_template = t
                    break

            for key in geocode_template.keys():
                if key in new_geocode_template:
                    geocode_template[key] = new_geocode_template[key]

            street = ""
            street_number = ""
            suburb = ""
            city = ""
            postcode = ""
            region = ""
            country = ""
            addressg = ""

            if geocode_template["provider"] == "osm":
                geocode_response = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={self.lat}&lon={self.lon}&format=json&accept_language={self.config.language}")

                addressg = geocode_response.json().get("display_name", "")
                street = geocode_response.json()["address"].get("road", "")
                street_number = geocode_response.json()["address"].get("house_number", "")
                postcode = geocode_response.json()["address"].get("postcode", "")
                region = geocode_response.json()["address"].get("state", "")
                country = geocode_response.json()["address"].get("country", "")

                city = geocode_response.json()["address"].get("city", "")
                if city == "":
                    city = geocode_response.json()["address"].get("town", "")
                    if city == "":
                        city = geocode_response.json()["address"].get("village", "")

                suburb = geocode_response.json()["address"].get("suburb", "")
                if suburb == "":
                    suburb = geocode_response.json()["address"].get("neighbourhood", "")

            elif geocode_template["provider"] == "mapbox":
                geocode_response = requests.get(f"https://api.mapbox.com/geocoding/v5/mapbox.places/{self.lon},{self.lat}.json?language={self.config.language}&access_token={geocode_template['key']}")
                
                for feature in geocode_response.json()["features"]:
                    if feature["place_type"] == "address":
                        addressg = feature["place_name"]
                        street = feature["text"]
                        street_number = feature["address"]
                    elif feature["place_type"] == "locality":
                        suburb = feature["text"]
                    elif feature["place_type"] == "place":
                        city = feature["text"]
                    elif feature["place_type"] == "postcode":
                        postcode = feature["text"]
                    elif feature["place_type"] == "region":
                        region = feature["text"]
                    elif feature["place_type"] == "country":
                        country = feature["text"]
  
            final_address = geocode_template["text"].format(address=addressg, street=street, street_number=street_number, city=city, suburb=suburb, postcode=postcode, region=region, country=country)
            address = f"{final_address}\n"

        # WP specific stuff
        if self.type == "portal":
            static_color = "c067fc"
            embed_color = 12609532
            embed_username = self.locale["portal_name"]
            embed_avatar = "https://raw.githubusercontent.com/ccev/stopwatcher-icons/master/portal.png"
            if self.edit:
                embed_username = self.locale["portal_edit_name"]
        elif self.type == "stop":
            static_color = "128fed"
            embed_color = 1216493
            embed_username = self.locale["stop_name"]
            embed_avatar = "https://raw.githubusercontent.com/ccev/stopwatcher-icons/master/stop.png"
            if self.edit:
                embed_username = self.locale["stop_edit_name"]
        elif self.type == "gym":
            static_color = "bac0c5"
            embed_color = 12239045
            embed_username = self.locale["gym_name"]
            embed_avatar = "https://raw.githubusercontent.com/ccev/stopwatcher-icons/master/gym.png"
            if self.edit:
                embed_username = self.locale["gym_edit_name"]

        # Static Map
        if self.config.use_static_map:
            static_map = StaticMap.create_static_map(self.config, self.queries, self.type, self.lat, self.lon, static_color)
        else:
            static_map = ""

        # Send
        if "webhook" in fil:
            data = {
                "username": embed_username,
                "avatar_url": embed_avatar,
                "embeds": [{
                    "title": title,
                    "description": f"{text}\n\n{address}{links}",
                    "color": embed_color,
                    "footer": {
                        "text": convert_time
                    },
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
            for char in ["_", "~", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
                text = text.replace(char, f"\\{char}")
                address = address.replace(char, f"\\{char}")
            text = text.replace("**", "*")
            for chat_id in fil["chat_id"]:
                if not self.empty:
                    payload = {"chat_id": str(chat_id), "photo": image}
                    result = requests.get(f"https://api.telegram.org/bot{fil['bot_id']}/sendPhoto", params = payload)
                    print(f"Result {result.status_code} for Photo")
                if not text == "":
                    text = f"\n\n{text}"
                payload = {"chat_id": str(chat_id), "parse_mode": "markdownv2", "text": f"*{embed_username}*\n{title}{text}\n\n[‌‌]({static_map}){address}{links}"}
                result = requests.get(f"https://api.telegram.org/bot{fil['bot_id']}/sendMessage", params = payload)
                print(f"Result {result.status_code} for Text")
                time.sleep(2)

    def send_location_edit(self, fil, old_lat, old_lon):
        print(f"Found edited location of {self.type} {self.name} - Sending now.")
        self.edit = True
        self.edit_type = "location"
        self.before_edit = [old_lat, old_lon]
        title = self.locale["location_edit_title"].format(name = self.name)
        text = self.locale["edit_text"].format(old = f"`{old_lat},{old_lon}`", new = f"`{self.lat},{self.lon}`")
        self.send(fil, text, title)

    def send_name_edit(self, fil, old_name):
        print(f"Found edited name of {self.type} {old_name} - Sending now.")
        self.edit = True
        self.edit_type = "name"
        self.before_edit = old_name
        title = self.locale["name_edit_title"].format(name = old_name)
        text = self.locale["edit_text"].format(old = f"`{old_name}`", new = f"`{self.name}`")
        self.send(fil, text, title)

    def send_img_edit(self, fil, old_img):
        print(f"Found new image for {self.type} {self.name} - Sending now.")
        self.edit = True
        self.edit_type = "img"
        self.before_edit = old_img
        title = self.locale["img_edit_title"].format(name = self.name)
        text = self.locale["edit_text"].format(old = f"[Link]({old_img})", new = f"[Link]({self.img})")
        self.send(fil, text, title)

    def send_deleted(self, fil):
        print(f"Found possibly removed {self.type} {self.name} :o")
        self.edit = True
        self.edit_type = "deleted"
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
