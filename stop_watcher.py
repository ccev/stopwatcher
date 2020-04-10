import json

from pymysql import connect

from util.config import create_config
from util.queries import create_queries
from util.waypoints import waypoint

config = create_config("config/config.ini")

mydb = connect(host = config.db_host, user = config.db_user, password = config.db_password, database = config.db_name_scan, port = config.db_port, autocommit = True)
cursor = mydb.cursor()

with open("config/filters.json", encoding="utf-8") as f:
    config.filters = json.load(f)

with open("config/geofence.json", encoding="utf-8") as f:
    config.geofences = json.load(f)

with open(f"locale/{config.language}.json", encoding="utf-8") as f:
    config.locale = json.load(f)

with open("config/cache/portals.json", encoding="utf-8") as f:
    portal_cache = json.load(f)

with open("config/cache/stops_full.json", encoding="utf-8") as f:
    full_stop_cache = json.load(f)

with open("config/cache/stops_empty.json", encoding="utf-8") as f:
    empty_stop_cache = json.load(f)

with open("config/cache/gyms_full.json", encoding="utf-8") as f:
    full_gym_cache = json.load(f)

with open("config/cache/gyms_empty.json", encoding="utf-8") as f:
    empty_gym_cache = json.load(f)

queries = create_queries(config, cursor)
print("Ready to watch Stops")

for fil in config.filters:
    print(f"Looking for things in {fil['area']}")
    dont_send_empty = True
    if "send_empty" in fil:
        if fil["send_empty"]:
            dont_send_empty = False

    if "update" in fil:
        if "stop" in fil["update"]:
            stops = queries.get_empty_stops(fil["area"])
            for s_id in stops:
                stop = waypoint(queries, config, "stop", s_id)
                stop.update()
        if "gym" in fil["update"]:
            gyms = queries.get_empty_gyms(fil["area"])
            for g_id in gyms:
                gym = waypoint(queries, config, "gym", g_id)
                gym.update()
    if "delete_converted_stops" in fil:
        if fil["delete_converted_stops"]:
            stops = queries.get_converted_stops(fil["area"])
            for s_id in stops:
                stop = waypoint(queries, config, "stop", s_id)
                #stop.delete()
    if "send" in fil:
        if "portal" in fil["send"]:
            portals = queries.get_portals(fil["area"])
            for p_id, p_lat, p_lon, p_name, p_img in portals:
                if not p_id in portal_cache:
                    portal = waypoint(queries, config, "portal", p_id, p_name, p_img, p_lat, p_lon)
                    portal.send(fil)
                    portal_cache.append(p_id)
        if "stop" in fil["send"]:
            stops = queries.get_stops(fil["area"])
            for s_id, s_lat, s_lon, s_name, s_img in stops:
                stop = waypoint(queries, config, "stop", s_id, s_name, s_img, s_lat, s_lon)
                if stop.empty:
                    if dont_send_empty:
                        continue
                    if not stop.id in empty_stop_cache:
                        stop.send(fil)
                        empty_stop_cache.append(stop.id)
                else:
                    if not stop.id in full_stop_cache:                       
                        stop.send(fil)
                        full_stop_cache.append(stop.id)
        if "gym" in fil["send"]:
            gyms = queries.get_gyms(fil["area"])
            for g_id, g_lat, g_lon, g_name, g_img in gyms:
                gym = waypoint(queries, config, "gym", g_id, g_name, g_img, g_lat, g_lon)
                if gym.empty:
                    if dont_send_empty:
                        continue
                    if not gym.id in empty_gym_cache:
                        gym.send(fil)
                        empty_gym_cache.append(g_id)
                else:
                    if not gym.id in full_gym_cache:
                        gym.send(fil)
                        full_gym_cache.append(g_id) 
    if "edits" in fil:
        if "portal" in fil["edits"]:
            continue

cursor.close()
mydb.close()