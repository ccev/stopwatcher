import json
import argparse
import sys

from pymysql import connect
from rich.console import Console
from rich.table import Column, Table
from rich.progress import Progress

import util.tools as tools
from util.config import create_config
from util.queries import create_queries
from util.waypoints import waypoint, init

config = create_config("config/config.ini")
config.console = Console()
config.console.log("Initializing...")

with open("config/filters.json", encoding="utf-8") as f:
    config.filters = json.load(f)

with open("config/areas.json" if config.geojson else "config/geofence.json", encoding="utf-8") as f:
    config.geofences = json.load(f)

with open("config/templates.json", encoding="utf-8") as f:
    config.templates = json.load(f)

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

with open("config/cache/deleted.json", encoding="utf-8") as f:
    deleted_cache = json.load(f)

with open("config_example/cache/edits.json", encoding="utf-8") as f:
    empty_edit_list = json.load(f)

mydb = connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_password,
    database=config.db_name_scan,
    port=config.db_port,
    autocommit=True
)
cursor = mydb.cursor()

mydb_p = connect(
    host=config.portal_db_host,
    user=config.portal_db_user,
    password=config.portal_db_password,
    database=config.db_name_portal,
    port=config.portal_db_port,
    autocommit=True
)
portal_cursor = mydb_p.cursor()
queries = create_queries(config, cursor, portal_cursor)
init = init(queries)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--init", action='store_true', help="Copy every missing Stop/Gym/Portal ID into Stop Watcher's cache files")
parser.add_argument("-d", "--delete", action='store_true', help="Generates SQL Queries to delete possibly removed Waypoints from you Databases")
parser.add_argument("-c", "--compare", action='store_true', help="Compare all your Stops/Gyms to Portals and update them if details don't match")
args = parser.parse_args()

if args.init:
    portal_cache = []
    full_stop_cache = []
    full_gym_cache = []
    edit_list = {"portals": {},"stops": {},"gyms": {}}

if args.delete:
    tools.delete(queries, config, deleted_cache)
    sys.exit()

if args.compare:
    tools.compare(queries, config)
    sys.exit()

if len(portal_cache) == 0:
    config.console.log("Found empty Portal Cache. Trying to fill it now.")
    try:
        portal_cache = init.write_portals(portal_cache)
    except:
        config.console.log("Error while doing that. Just skipping it.")

if len(full_stop_cache) == 0 or len(empty_stop_cache) == 0:
    config.console.log("Found empty Stop Cache. Trying to fill it now.")
    try:
        full_stop_cache = init.write_stops(full_stop_cache)
        empty_stop_cache = full_stop_cache
    except:
        config.console.log("Error while doing that. Just skipping it.")   

if len(full_gym_cache) == 0 or len(empty_gym_cache) == 0:
    config.console.log("Found empty Gym Cache. Trying to fill it now.")
    try:
        full_gym_cache = init.write_gyms(full_gym_cache)
        empty_gym_cache = full_gym_cache
    except:
        config.console.log("Error while doing that. Just skipping it.")

if (len(edit_list["portals"]) + len(edit_list["stops"]) + len(edit_list["gyms"])) == 0:
    config.console.log("Found empty Edit Cache. Trying to fill it now.")
    edit_list = queries.create_edit_list(empty_edit_list, edit_list)

new_portal_cache = portal_cache.copy()
new_full_stop_cache = full_stop_cache.copy()
new_empty_stop_cache = empty_stop_cache.copy()
new_full_gym_cache = full_gym_cache.copy()
new_empty_gym_cache = empty_gym_cache.copy()
new_deleted_cache = deleted_cache.copy()

def check_edits(fil, wp, w_type, w_id, w_lat, w_lon, w_name, w_img):
    if wp is None:
        return
    if (w_lat != wp[0]) or (w_lon != wp[1]):
        if "location" in fil["edit_types"]:
            _waypoint = waypoint(queries, config, w_type, w_id, wp[2], wp[3], wp[0], wp[1])
            _waypoint.send_location_edit(fil, w_lat, w_lon)
    if w_name is None or w_img is None or wp[2] is None or wp[3] is None:
        return
    if w_name.replace(" ", "").strip() != wp[2].replace(" ", "").strip():
        if "title" in fil["edit_types"]:
            _waypoint = waypoint(queries, config, w_type, w_id, wp[2], wp[3], wp[0], wp[1])
            _waypoint.send_name_edit(fil, w_name)
            if not w_type == "gym":
                if "update_gym_title" in fil:
                    if fil["update_gym_title"]:
                        if _waypoint.is_gym():
                            _waypoint.set_type("gym")
                            _waypoint.update(False)
    if w_img != wp[3]:
        if "photo" in fil["edit_types"]:
            _waypoint = waypoint(queries, config, w_type, w_id, wp[2], wp[3], wp[0], wp[1])
            _waypoint.send_img_edit(fil, w_img)

log_filters = [
    ["update", "What to update upon creation"],
    ["delete_converted_stops", "Delete converted Stops"],
    ["send", "What to send notifications for"],
    ["send_empty", "Should they be sent with an unknown image/name?"],
    ["edits", "What to track edits for"],
    ["edit_types", "What kind of edits to track"],
    ["update_gym_title", "If a Portal's title changes, should the corresponding Gym title get updated?"]
]

config.console.log("Done. Ready to watch Stops")

for fil in config.filters:
    #print("----------------------------")
    #print(f"Going through {fil['area']}")
    #print("")
    config.console.log(f"[green]> Now going through [bold]{fil['area'].capitalize()}")
    table = Table(show_header=False)
    table.add_column("key")
    table.add_column("value")
    for logfilter in log_filters:
        value = fil.get(logfilter[0], None)
        if isinstance(value, list):
            value = ", ".join(value)
        table.add_row(logfilter[1], str(value))
    config.console.log(table)

    dont_send_empty = True
    if "send_empty" in fil:
        if fil["send_empty"]:
            dont_send_empty = False

    deleted_max_portals = 5
    deleted_timespan_portals = ((4*config.scraper_wait) / 60)
    deleted_max_stops = 5
    deleted_timespan_stops = ((4*config.removed_wait) / 60)
    if "deleted" in fil:
        if "max" in fil["deleted"]:
            if "scraper" in fil["deleted"]["max"]:
                deleted_max_portals = fil["deleted"]["max"]["scraper"]
            if "scanner" in fil["deleted"]["max"]:
                deleted_max_stops = fil["deleted"]["max"]["scanner"]
        if "timespan" in fil["deleted"]:
            if "scraper" in fil["deleted"]["timespan"]:
                deleted_timespan_portals = fil["deleted"]["timespan"]["scraper"]
            if "scanner" in fil["deleted"]["timespan"]:
                deleted_timespan_stops = fil["deleted"]["timespan"]["scanner"]

    if "update" in fil:
        if "stop" in fil["update"]:
            config.console.log("Looking for Stops to update")
            stops = queries.get_empty_stops(fil["area"])
            for s_id in stops:
                stop = waypoint(queries, config, "stop", s_id[0])
                stop.update()
        if "gym" in fil["update"]:
            config.console.log("Looking for Gyms to update")
            gyms = queries.get_empty_gyms(fil["area"])
            for g_id in gyms:
                gym = waypoint(queries, config, "gym", g_id[0])
                gym.update()
    if "delete_converted_stops" in fil:
        if fil["delete_converted_stops"]:
            config.console.log("Looking for converted Stops to delete")
            stops = queries.get_converted_stops(fil["area"])
            for s_id, s_name in stops:
                stop = waypoint(queries, config, "stop", s_id, s_name)
                stop.delete()
    if "send" in fil:
        if "portal" in fil["send"]:
            config.console.log("Looking for new Portals")
            portals = queries.get_portals(fil["area"])
            for p_id, p_lat, p_lon, p_name, p_img in portals:
                if not p_id in portal_cache:
                    portal = waypoint(queries, config, "portal", p_id, p_name, p_img, p_lat, p_lon)
                    portal.send(fil)
                    if not portal.id in new_portal_cache:
                        new_portal_cache.append(p_id)
            with open("config/cache/portals.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(new_portal_cache, indent=4))

        if "stop" in fil["send"]:
            config.console.log("Looking for new Stops")
            stops = queries.get_stops(fil["area"])
            for s_id, s_lat, s_lon, s_name, s_img in stops:
                stop = waypoint(queries, config, "stop", s_id, s_name, s_img, s_lat, s_lon)
                if stop.empty:
                    if dont_send_empty:
                        continue
                    if not stop.id in empty_stop_cache:
                        stop.send(fil)
                        if not stop.id in new_empty_stop_cache:
                            new_empty_stop_cache.append(stop.id)
                else:
                    if not stop.id in full_stop_cache:                       
                        stop.send(fil)
                        if not stop.id in new_full_stop_cache:
                            new_full_stop_cache.append(stop.id)
            with open("config/cache/stops_full.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(new_full_stop_cache, indent=4))

            with open("config/cache/stops_empty.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(new_empty_stop_cache, indent=4))

        if "gym" in fil["send"]:
            config.console.log("Looking for new Gyms")
            gyms = queries.get_gyms(fil["area"])
            for g_id, g_lat, g_lon, g_name, g_img in gyms:
                gym = waypoint(queries, config, "gym", g_id, g_name, g_img, g_lat, g_lon)
                if gym.empty:
                    if dont_send_empty:
                        continue
                    if not gym.id in empty_gym_cache:
                        gym.send(fil)
                        if not gym.id in new_empty_gym_cache:
                            new_empty_gym_cache.append(g_id)
                else:
                    if not gym.id in full_gym_cache:
                        gym.send(fil)
                        if not gym.id in new_full_gym_cache:
                            new_full_gym_cache.append(g_id)
            with open("config/cache/gyms_full.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(new_full_gym_cache, indent=4))

            with open("config/cache/gyms_empty.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(new_empty_gym_cache, indent=4))

    if "edits" in fil:
        if "portal" in fil["edits"]:
            with Progress(console=config.console) as progress:
                task = progress.add_task("Looking for Portal Edits", total=len(edit_list["portals"][fil["area"]]))
                for p_id, p_lat, p_lon, p_name, p_img in edit_list["portals"][fil["area"]]:
                    p = queries.get_full_portal_by_id(p_id)
                    #0=lat, 1=lon, 2=name, 3=img
                    check_edits(fil, p, "portal", p_id, p_lat, p_lon, p_name, p_img)
                    progress.update(task, advance=1)

            if "removal" in fil["edit_types"]:
                config.console.log("Looking for Portal Removals")
                portals = queries.get_deleted_portals(deleted_timespan_portals, fil["area"])
                if len(portals) <= deleted_max_portals:
                    for p_id, p_lat, p_lon, p_name, p_img in portals:
                        if not p_id in deleted_cache["portals"]:
                            portal = waypoint(queries, config, "portal", p_id, p_name, p_img, p_lat, p_lon)
                            portal.send_deleted(fil)
                            if not p_id in new_deleted_cache["portals"]:
                                new_deleted_cache["portals"].append(p_id)
                else:
                    config.console.log(f"Deleted Portal amount exceeded the limit of {deleted_max_portals} - Check your Cookie")
              
        if "stop" in fil["edits"]:
            with Progress(console=config.console) as progress:
                task = progress.add_task("Looking for Stop Edits", total=len(edit_list["stops"][fil["area"]]))
                for s_id, s_lat, s_lon, s_name, s_img in edit_list["stops"][fil["area"]]:
                    s = queries.get_full_stop_by_id(s_id)
                    #0=lat, 1=lon, 2=name, 3=img
                    check_edits(fil, s, "stop", s_id, s_lat, s_lon, s_name, s_img)
                    progress.update(task, advance=1)

            if "removal" in fil["edit_types"]:
                config.console.log("Looking for Stop Removals")
                stops = queries.get_deleted_stops(deleted_timespan_stops, fil["area"])
                if len(stops) <= deleted_max_stops:
                    for s_id, s_lat, s_lon, s_name, s_img in stops:
                        if not s_id in deleted_cache["stops"]:
                            stop = waypoint(queries, config, "stop", s_id, s_name, s_img, s_lat, s_lon)
                            stop.send_deleted(fil)
                            if not s_id in new_deleted_cache["stops"]:
                                new_deleted_cache["stops"].append(s_id)
                else:
                    config.console.log(f"Stop amount exceeded the limit of {deleted_max_portals} - Check your Scanner Setup")
        
        if "gym" in fil["edits"]:
            with Progress(console=config.console) as progress:
                task = progress.add_task("Looking for Gym Edits", total=len(edit_list["gyms"][fil["area"]]))
                for g_id, g_lat, g_lon, g_name, g_img in edit_list["gyms"][fil["area"]]:
                    g = queries.get_full_gym_by_id(g_id)
                    #0=lat, 1=lon, 2=name, 3=img
                    check_edits(fil, g, "gym", g_id, g_lat, g_lon, g_name, g_img)
                    progress.update(task, advance=1)

            if "removal" in fil["edit_types"]:
                config.console.log("Looking for Gym Removals")
                gyms = queries.get_deleted_gyms(deleted_timespan_stops, fil["area"])
                if len(gyms) <= deleted_max_stops:
                    for g_id, g_lat, g_lon, g_name, g_img in gyms:
                        if not g_id in deleted_cache["gyms"]:
                            gym = waypoint(queries, config, "gym", g_id, g_name, g_img, g_lat, g_lon)
                            gym.send_deleted(fil)
                            if not g_id in new_deleted_cache["gyms"]:
                                new_deleted_cache["gyms"].append(g_id)
                else:
                    config.console.log(f"Gym amount exceeded the limit of {deleted_max_portals} - Check your Scanner Setup")

if any("edits" in i for i in config.filters):
    config.console.log("Writing Edit Cache")
    edit_list = queries.create_edit_list(empty_edit_list, edit_list)

cursor.close()
mydb.close()
mydb_p.close()

with open("config/cache/edits.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(edit_list, indent=4))

with open("config/cache/deleted.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(new_deleted_cache, indent=4))

config.console.log("[green]Done.[/] Thanks for using Stop Watcher")
