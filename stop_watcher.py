import json
import argparse
import sys

from pymysql import connect

from util.config import create_config
from util.queries import create_queries
from util.waypoints import waypoint, init

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

with open("config/cache/edits.json", encoding="utf-8") as f:
    edit_list = json.load(f)

with open("config_example/cache/edits.json", encoding="utf-8") as f:
    empty_edit_list = json.load(f)

queries = create_queries(config, cursor)
init = init(queries)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--init", action='store_true', help="Copy every missing Stop/Gym/Portal ID into Stop Watcher's cache files")
args = parser.parse_args()

if args.init:
    portal_cache = json.loads("[]")
    full_stop_cache = json.loads("[]")
    full_gym_cache = json.loads("[]")

if len(portal_cache) == 0:
    print("Found empty Portal Cache. Trying to fill it now.")
    try:
        portal_cache = init.write_portals(portal_cache)
    except:
        print("Error while doing that. Just skipping it.")

if len(full_stop_cache) == 0 or len(empty_stop_cache) == 0:
    print("Found empty Stop Cache. Trying to fill it now.")
    try:
        full_stop_cache = init.write_stops(full_stop_cache) 
        empty_stop_cache = full_stop_cache  
    except:
        print("Error while doing that. Just skipping it.")   

if len(full_gym_cache) == 0 or len(empty_gym_cache) == 0:
    print("Found empty Gym Cache. Trying to fill it now.")
    try:
        full_gym_cache = init.write_gyms(full_gym_cache) 
        empty_gym_cache = full_gym_cache   
    except:
        print("Error while doing that. Just skipping it.")

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
                stop = waypoint(queries, config, "stop", s_id[0])
                stop.update()
        if "gym" in fil["update"]:
            gyms = queries.get_empty_gyms(fil["area"])
            for g_id in gyms:
                gym = waypoint(queries, config, "gym", g_id[0])
                gym.update()
    if "delete_converted_stops" in fil:
        if fil["delete_converted_stops"]:
            stops = queries.get_converted_stops(fil["area"])
            for s_id, s_name in stops:
                stop = waypoint(queries, config, "stop", s_id, s_name)
                stop.delete()
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
            for p_id, p_lat, p_lon, p_name, p_img in edit_list["portals"]:
                p = queries.get_full_portal_by_id(p_id)
                #0=lat, 1=lon, 2=name, 3=img
                if (p_lat != p[0]) or (p_lon != p[1]):
                    if "location" in fil["edit_types"]:
                        portal = waypoint(queries, config, "portal", p_id, p[2], p[3], p[0], p[1])
                        portal.send_location_edit(fil, p_lat, p_lon)
                if p_name != p[2]:
                    if "title" in fil["edit_types"]:
                        portal = waypoint(queries, config, "portal", p_id, p[2], p[3], p[0], p[1])
                        portal.send_name_edit(fil, p_name)
                if p_img != p[3]:
                    if "photo" in fil["edit_types"]:
                        portal = waypoint(queries, config, "portal", p_id, p[2], p[3], p[0], p[1])
                        portal.send_name_edit(fil, p_img)
        if "stop" in fil["edits"]:
            for s_id, s_lat, s_lon, s_name, s_img in edit_list["stops"]:
                s = queries.get_full_stos_by_id(s_id)
                #0=lat, 1=lon, 2=name, 3=img
                if (s_lat != s[0]) or (s_lon != s[1]):
                    if "location" in fil["edit_types"]:
                        stop = waypoint(queries, config, "stop", s_id, s[2], s[3], s[0], s[1])
                        stop.send_location_edit(fil, s_lat, s_lon)
                if s_name != s[2]:
                    if "title" in fil["edit_types"]:
                        stop = waypoint(queries, config, "stop", s_id, s[2], s[3], s[0], s[1])
                        stop.send_name_edit(fil, s_name)
                if s_img != s[3]:
                    if "photo" in fil["edit_types"]:
                        stop = waypoint(queries, config, "stop", s_id, s[2], s[3], s[0], s[1])
                        stop.send_name_edit(fil, s_img)
        if "gym" in fil["edits"]:
            for g_id, g_lat, g_lon, g_name, g_img in edit_list["gyms"]:
                s = queries.get_full_stog_by_id(g_id)
                #0=lat, 1=lon, 2=name, 3=img
                if (g_lat != g[0]) or (g_lon != g[1]):
                    if "location" in fil["edit_types"]:
                        gym = waypoint(queries, config, "gym", g_id, g[2], g[3], g[0], g[1])
                        gym.send_location_edit(fil, g_lat, g_lon)
                if g_name != g[2]:
                    if "title" in fil["edit_types"]:
                        gym = waypoint(queries, config, "gym", g_id, g[2], g[3], g[0], g[1])
                        gym.send_name_edit(fil, g_name)
                if g_img != g[3]:
                    if "photo" in fil["edit_types"]:
                        gym = waypoint(queries, config, "gym", g_id, g[2], g[3], g[0], g[1])
                        gym.send_name_edit(fil, g_img)

if any("edits" in i for i in config.filters):
    edit_list = queries.create_edit_list(empty_edit_list)

cursor.close()
mydb.close()

with open("config/cache/portals.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(portal_cache, indent=4))

with open("config/cache/stops_full.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(full_stop_cache, indent=4))

with open("config/cache/stops_empty.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(empty_stop_cache, indent=4))

with open("config/cache/gyms_full.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(full_gym_cache, indent=4))

with open("config/cache/gyms_empty.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(empty_gym_cache, indent=4))

with open("config/cache/edits.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(edit_list, indent=4))