# -*- coding: utf-8 -*-

import time
import requests
import argparse

from pymysql import connect

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

DEFAULT_CONFIG = "default.ini"

### Queries
QUERY_CHECK = """SELECT {db_id}, {db_lat}, {db_lon}, {db_name}, {db_img} FROM {db_dbname}.{db_table}
WHERE (
    {db_lat} >= {lat_small} AND {db_lat} <= {lat_big}
  AND
    {db_lon} >= {lon_small} AND {db_lon} <= {lon_big}
)
"""
QUERY_CHECK_GYMS_MAD = """SELECT {db_gymdetails_table}.{db_gym_id}, {db_gym_lat}, {db_gym_lon}, {db_gym_name}, {db_gym_img} FROM {db_dbname}.{db_gym_table}
RIGHT JOIN {db_gymdetails_table} ON {db_gym_table}.{db_gym_id} = {db_gymdetails_table}.{db_gym_id}
WHERE (
    {db_gym_lat} >= {lat_small} AND {db_gym_lat} <= {lat_big}
  AND
    {db_gym_lon} >= {lon_small} AND {db_gym_lon} <= {lon_big}
)
"""
QUERY_UPDATE = """UPDATE {db_dbname}.{db_table}
SET
    {db_img} = '{img}',
    {db_name} = '{name}'
WHERE (
    {db_id} = '{id}'
)
"""
QUERY_EXIST = """SELECT {db_name}, {db_img} FROM {db_dbname}.{db_table}
WHERE (
    {db_lat} = {lat} AND {db_lon} = {lon}
)
"""
QUERY_DELETE_STOP = """DELETE FROM {db_dbname}.{db_stop_table}
WHERE (
    {db_stop_lat} = {lat} AND {db_stop_lon} = {lon}
)
"""

def create_config(config_path):
    config = dict()
    config_raw = ConfigParser()
    config_raw.read(DEFAULT_CONFIG)
    config_raw.read(config_path)
    ### Config
    config['send_stops'] = config_raw.getboolean(
        'Config',
        'STOPS')
    config['send_gyms'] = config_raw.getboolean(
        'Config',
        'GYMS')
    config['send_portals'] = config_raw.getboolean(
        'Config',
        'PORTALS')
    config['update_gym_stop'] = config_raw.getboolean(
        'Config',
        'GYM_UPDATE_THROUGH_STOP')
    config['update_gym_portal'] = config_raw.getboolean(
        'Config',
        'GYM_UPDATE_THROUGH_PORTAL')
    config['update_stop_portal'] = config_raw.getboolean(
        'Config',
        'STOP_UPDATE_THROUGH_PORTAL')
    config['delete_stops'] = config_raw.getboolean(
        'Config',
        'DELETE_CONVERTED_STOP')
    config['webhook_url_stop'] = config_raw.get(
        'Config',
        'STOP_WEBHOOK')
    config['webhook_url_gym'] = config_raw.get(
        'Config',
        'GYM_WEBHOOK')
    config['webhook_url_portal'] = config_raw.get(
        'Config',
        'PORTAL_WEBHOOK')
    config['lat_small'] = config_raw.getfloat(
        'Config',
        'MIN_LAT')
    config['lat_big'] = config_raw.getfloat(
        'Config',
        'MAX_LAT')
    config['lon_small'] = config_raw.getfloat(
        'Config',
        'MIN_LON')
    config['lon_big'] = config_raw.getfloat(
        'Config',
        'MAX_LON')
    config['dosleep'] = config_raw.getboolean(
        'Config',
        'LOOP')
    config['sleeptime'] = config_raw.getint(
        'Config',
        'SECONDS_BETWEEN_LOOPS')
    ### Embeds
    config['stop_img'] = config_raw.get(
        'Embeds',
        'STOP_IMAGE')
    config['stop_full_username'] = config_raw.get(
        'Embeds',
        'STOP_DETAILS_USERNAME')
    config['stop_unfull_username'] = config_raw.get(
        'Embeds',
        'STOP_NO_DETAILS_USERNAME')
    config['gym_img'] = config_raw.get(
        'Embeds',
        'GYM_IMAGE')
    config['gym_full_username'] = config_raw.get(
        'Embeds',
        'GYM_DETAILS_USERNAME')
    config['gym_unfull_username'] = config_raw.get(
        'Embeds',
        'GYM_NO_DETAILS_USERNAME')
    config['portal_img'] = config_raw.get(
        'Embeds',
        'PORTAL_IMAGE')
    config['portal_username'] = config_raw.get(
        'Embeds',
        'PORTAL_USERNAME')
    ### Static Map
    config['google_static'] = config_raw.getboolean(
        'Static Map',
        'ENABLE')
    config['google_api_key'] = config_raw.get(
        'Static Map',
        'G_API_KEY')
    config['google_zoom'] = config_raw.getint(
        'Static Map',
        'G_ZOOM')
    config['google_res'] = config_raw.get(
        'Static Map',
        'G_RESOLUTION')
    config['google_marker_size'] = config_raw.get(
        'Static Map',
        'G_MARKER_SIZE')
    config['google_marker_color_stop'] = config_raw.get(
        'Static Map',
        'G_MARKER_COLOR_STOP')
    config['google_marker_color_gym'] = config_raw.get(
        'Static Map',
        'G_MARKER_COLOR_GYM')
    config['google_marker_color_portal'] = config_raw.get(
        'Static Map',
        'G_MARKER_COLOR_PORTAL')
    ### DATABASE
    config['db_scan_schema'] = config_raw.get(
        'DB',
        'SCANNER_DB')
    config['db_portal_schema'] = config_raw.get(
        'DB',
        'PORTAL_DB')
    config['db_host'] = config_raw.get(
        'DB',
        'HOST')
    config['db_port'] = config_raw.getint(
        'DB',
        'PORT')
    config['db_user'] = config_raw.get(
        'DB',
        'USER')
    config['db_pass'] = config_raw.get(
        'DB',
        'PASSWORD')
    config['db_portal_dbname'] = config_raw.get(
        'DB',
        'PORTAL_DB_NAME')
    config['db_dbname'] = config_raw.get(
        'DB',
        'NAME')
    config['db_stop_table'] = config_raw.get(
        'DB',
        'POKESTOP_TABLE')
    config['db_stop_id'] = config_raw.get(
        'DB',
        'POKESTOP_ID')
    config['db_stop_lat'] = config_raw.get(
        'DB',
        'POKESTOP_LAT')
    config['db_stop_lon'] = config_raw.get(
        'DB',
        'POKESTOP_LON')
    config['db_stop_name'] = config_raw.get(
        'DB',
        'POKESTOP_NAME')
    config['db_stop_img'] = config_raw.get(
        'DB',
        'POKESTOP_IMAGE')
    config['db_gym_table'] = config_raw.get(
        'DB',
        'GYM_TABLE')
    config['db_gymdetails_table'] = config_raw.get(
        'DB',
        'GYMDETAILS_TABLE')
    config['db_gym_id'] = config_raw.get(
        'DB',
        'GYM_ID')
    config['db_gym_lat'] = config_raw.get(
        'DB',
        'GYM_LAT')
    config['db_gym_lon'] = config_raw.get(
        'DB',
        'GYM_LON')
    config['db_gym_name'] = config_raw.get(
        'DB',
        'GYM_NAME')
    config['db_gym_img'] = config_raw.get(
        'DB',
        'GYM_IMAGE')
    config['db_portal_table'] = config_raw.get(
        'DB',
        'PORTAL_TABLE')
    config['db_portal_id'] = config_raw.get(
        'DB',
        'PORTAL_ID')
    config['db_portal_lat'] = config_raw.get(
        'DB',
        'PORTAL_LAT')
    config['db_portal_lon'] = config_raw.get(
        'DB',
        'PORTAL_LON')
    config['db_portal_name'] = config_raw.get(
        'DB',
        'PORTAL_NAME')
    config['db_portal_img'] = config_raw.get(
        'DB',
        'PORTAL_IMAGE')

    return config

def connect_db(config):
    print("Connecting to DB")
    mydb = connect(
        host=config['db_host'],
        user=config['db_user'],
        passwd=config['db_pass'],
        database=config['db_dbname'],
        port=config['db_port'],
        autocommit=True)

    cursor = mydb.cursor()

    return cursor

def db_config(config):
    if config['db_scan_schema'] == "mad":
        config['db_stop_table'] = "pokestop"
        config['db_stop_id'] = "pokestop_id"
        config['db_stop_lat'] = "latitude"
        config['db_stop_lon'] = "longitude"
        config['db_stop_name'] = "name"
        config['db_stop_img'] = "image"

        config['db_gym_table'] = "gym"
        config['db_gymdetails_table'] = "gymdetails"
        config['db_gym_id'] = "gym_id"
        config['db_gym_lat'] = "latitude"
        config['db_gym_lon'] = "longitude"
        config['db_gym_name'] = "name"
        config['db_gym_img'] = "url"

    if config['db_scan_schema'] == "rdm":
        config['db_stop_table'] = "pokestop"
        config['db_stop_id'] = "id"
        config['db_stop_lat'] = "lat"
        config['db_stop_lon'] = "lon"
        config['db_stop_name'] = "name"
        config['db_stop_img'] = "url"

        config['db_gym_table'] = "gym"
        config['db_gymdetails_table'] = "doesntmatter"
        config['db_gym_id'] = "id"
        config['db_gym_lat'] = "lat"
        config['db_gym_lon'] = "lon"
        config['db_gym_name'] = "name"
        config['db_gym_img'] = "url"

    if config['db_portal_schema'] == "pmsf":
        config['db_portal_table'] = "ingress_portals"
        config['db_portal_id'] = "external_id"
        config['db_portal_lat'] = "lat"
        config['db_portal_lon'] = "lon"
        config['db_portal_name'] = "name"
        config['db_portal_img'] = "url"

def get_portals():
    return open("txt/portals.txt", "r").read().splitlines()

def get_stops_full():
    return open("txt/stop_full.txt", "r").read().splitlines()

def get_stops_unfull():
    return open("txt/stop_unfull.txt", "r").read().splitlines()

def get_gyms_unfull():
    return open("txt/gym_unfull.txt", "r").read().splitlines()

def get_gyms_full():
    return open("txt/gym_full.txt", "r").read().splitlines()


def send_webhook_portal(db_portal_id, db_portal_lat, db_portal_lon, db_portal_name, db_portal_img, config):
    google_zoom = config['google_zoom']
    google_res = config['google_res']
    google_api_key = config['google_api_key']
    google_marker_size = config['google_marker_size']
    google_marker_color_portal = config['google_marker_color_portal']
    navigation = f"[Google Maps](https://www.google.com/maps/search/?api=1&query={db_portal_lat},{db_portal_lon}) | [Intel](https://intel.ingress.com/intel?ll={db_portal_lat},{db_portal_lon}&z=15&pll={db_portal_lat},{db_portal_lon})"
    if config['google_static']:
        static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={db_portal_lat},{db_portal_lon}&zoom={google_zoom}&scale=1&size={google_res}&maptype=roadmap&key={google_api_key}&format=png&visual_refresh=true&markers=size:{google_marker_size}%7Ccolor:{google_marker_color_portal}%7Clabel:%7C{db_portal_lat},{db_portal_lon}"
        data = {
            "username": config['portal_username'],
            "avatar_url": config['portal_img'],
            "embeds": [{
                "thumbnail": {
                    "url": db_portal_img
                },
                "image": {
                    "url": static_map
                },
                "fields": [
                    {
                    "name": db_portal_name,
                    "value": navigation
                    }
                ]
            }]
        }
    else:
        data = {
            "username": config['portal_username'],
            "avatar_url": config['portal_img'],
            "embeds": [{
                "thumbnail": {
                    "url": db_portal_img
                },
                "fields": [
                    {
                    "name": db_portal_name,
                    "value": navigation
                    }
                ]
            }]
        }
    result = requests.post(config['webhook_url_portal'], json=data)
    print(f"Portal Webhook: {result}")

    with open("txt/portals.txt", "a") as f:
        f.write(db_portal_id + "\n")

def send_webhook_stop_full(db_stop_id, db_stop_lat, db_stop_lon, db_stop_name, db_stop_img, config):
    google_zoom = config['google_zoom']
    google_res = config['google_res']
    google_api_key = config['google_api_key']
    google_marker_size = config['google_marker_size']
    google_marker_color_stop = config['google_marker_color_stop']
    navigation = f"[Google Maps](https://www.google.com/maps/search/?api=1&query={db_stop_lat},{db_stop_lon})"
    if config['google_static']: 
        static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={db_stop_lat},{db_stop_lon}&zoom={google_zoom}&scale=1&size={google_res}&maptype=roadmap&key={google_api_key}&format=png&visual_refresh=true&markers=size:{google_marker_size}%7Ccolor:{google_marker_color_stop}%7Clabel:%7C{db_stop_lat},{db_stop_lon}"
        data = {
            "username": config['stop_full_username'],
            "avatar_url": config['stop_img'],
            "embeds": [{
                "thumbnail": {
                    "url": db_stop_img
                },
                "image": {
                    "url": static_map
                },
                "fields": [
                    {
                    "name": db_stop_name,
                    "value": navigation
                    }
                ]
            }]
        }
    else:
        data = {
            "username": config['stop_full_username'],
            "avatar_url": config['stop_img'],
            "embeds": [{
                "thumbnail": {
                    "url": db_stop_img
                },
                "fields": [
                    {
                    "name": db_stop_name,
                    "value": navigation
                    }
                ]
            }]
        }
    result = requests.post(config['webhook_url_stop'], json=data)
    print(f"Full stop webhook: {result}")

    with open("txt/stop_full.txt", "a") as f:
        f.write(db_stop_id + "\n")

def send_webhook_stop_unfull(db_stop_id, db_stop_lat, db_stop_lon, config):
    google_zoom = config['google_zoom']
    google_res = config['google_res']
    google_api_key = config['google_api_key']
    google_marker_size = config['google_marker_size']
    google_marker_color_stop = config['google_marker_color_stop']
    navigation = f"https://www.google.com/maps/search/?api=1&query={db_stop_lat},{db_stop_lon}"
    if config['google_static']:
        static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={db_stop_lat},{db_stop_lon}&zoom={google_zoom}&scale=1&size={google_res}&maptype=roadmap&key={google_api_key}&format=png&visual_refresh=true&markers=size:{google_marker_size}%7Ccolor:{google_marker_color_stop}%7Clabel:%7C{db_stop_lat},{db_stop_lon}"
        data = {
            "username": config['stop_unfull_username'],
            "avatar_url": config['stop_img'],
            "embeds": [{
                "title": "Google Maps",
                "url": navigation,
                "image": {
                    "url": static_map
                }
            }]
        }
    else:
        data = {
            "username": config['stop_unfull_username'],
            "avatar_url": config['stop_img'],
            "embeds": [{
                "title": "Google Maps",
                "url": navigation
            }]
        }
    result = requests.post(config['webhook_url_stop'], json=data)
    print(f"Unfull stop webhook: {result}")

    with open("txt/stop_unfull.txt", "a") as f:
        f.write(db_stop_id + "\n")

def send_webhook_gym_full(db_gym_id, db_gym_lat, db_gym_lon, db_gym_name, db_gym_img, config):
    google_zoom = config['google_zoom']
    google_res = config['google_res']
    google_api_key = config['google_api_key']
    google_marker_size = config['google_marker_size']
    google_marker_color_gym = config['google_marker_color_gym']
    navigation = f"[Google Maps](https://www.google.com/maps/search/?api=1&query={db_gym_lat},{db_gym_lon})"
    if config['google_static']:
        static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={db_gym_lat},{db_gym_lon}&zoom={google_zoom}&scale=1&size={google_res}&maptype=roadmap&key={google_api_key}&format=png&visual_refresh=true&markers=size:{google_marker_size}%7Ccolor:{google_marker_color_gym}%7Clabel:%7C{db_gym_lat},{db_gym_lon}"
        data = {
            "username": config['gym_full_username'],
            "avatar_url": config['gym_img'],
            "embeds": [{
                "thumbnail": {
                    "url": db_gym_img
                },
                "image": {
                    "url": static_map
                },
                "fields": [
                    {
                    "name": db_gym_name,
                    "value": navigation
                    }
                ]
            }]
        }
    else:
        data = {
            "username": config['gym_full_username'],
            "avatar_url": config['gym_img'],
            "embeds": [{
                "thumbnail": {
                    "url": db_gym_img
                },
                "fields": [
                    {
                    "name": db_gym_name,
                    "value": navigation
                    }
                ]
            }]
        }
    result = requests.post(config['webhook_url_gym'], json=data)
    print(f"Full gym webhook: {result}")

    with open("txt/gym_full.txt", "a") as f:
        f.write(db_gym_id + "\n")

def send_webhook_gym_unfull(db_gym_id, db_gym_lat, db_gym_lon, config):
    google_zoom = config['google_zoom']
    google_res = config['google_res']
    google_api_key = config['google_api_key']
    google_marker_size = config['google_marker_size']
    google_marker_color_gym = config['google_marker_color_gym']
    navigation = f"https://www.google.com/maps/search/?api=1&query={db_gym_lat},{db_gym_lon}"
    static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={db_gym_lat},{db_gym_lon}&zoom={google_zoom}&scale=1&size={google_res}&maptype=roadmap&key={google_api_key}&format=png&visual_refresh=true&markers=size:{google_marker_size}%7Ccolor:{google_marker_color_gym}%7Clabel:%7C{db_gym_lat},{db_gym_lon}"
    if config['google_static']:
        static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={db_gym_lat},{db_gym_lon}&zoom={google_zoom}&scale=1&size={google_res}&maptype=roadmap&key={google_api_key}&format=png&visual_refresh=true&markers=size:{google_marker_size}%7Ccolor:{google_marker_color_gym}%7Clabel:%7C{db_gym_lat},{db_gym_lon}"
        data = {
            "username": config['gym_unfull_username'],
            "avatar_url": config['gym_img'],
            "embeds": [{
                "title": "Google Maps",
                "url": navigation,
                "image": {
                    "url": static_map
                }
            }]
        }
    else:
        data = {
            "username": config['gym_unfull_username'],
            "avatar_url": config['gym_img'],
            "embeds": [{
                "title": "Google Maps",
                "url": navigation
            }]
        }
    result = requests.post(config['webhook_url_gym'], json=data)
    print(f"Unfull gym webhook: {result}")

    with open("txt/gym_unfull.txt", "a") as f:
        f.write(db_gym_id + "\n")

def check_portals(cursor, config):
    if config['send_portals']:
        print("Checking for new portals")
        check_portals_query = QUERY_CHECK.format(
            db_id=config['db_portal_id'],
            db_lat=config['db_portal_lat'],
            db_lon=config['db_portal_lon'],
            db_name=config['db_portal_name'],
            db_img=config['db_portal_img'],
            db_dbname=config['db_portal_dbname'],
            db_table=config['db_portal_table'],
            lat_small=config['lat_small'],
            lat_big=config['lat_big'],
            lon_small=config['lon_small'],
            lon_big=config['lon_big']
        )
        cursor.execute(check_portals_query)
        result_portals = cursor.fetchall()

        for db_portal_id, db_portal_lat, db_portal_lon, db_portal_name, db_portal_img in result_portals:
            if not db_portal_id in get_portals():
                print("sending portal: ", db_portal_name)
                send_webhook_portal(db_portal_id, db_portal_lat, db_portal_lon, db_portal_name, db_portal_img, config)
                time.sleep(1)

def update_stop_portal(cursor, config):
    if config['update_stop_portal']:
        print("Checking if a stop can be updated")
        check_stops_query = QUERY_CHECK.format(
            db_id=config['db_stop_id'],
            db_lat=config['db_stop_lat'],
            db_lon=config['db_stop_lon'],
            db_name=config['db_stop_name'],
            db_img=config['db_stop_img'],
            db_dbname=config['db_dbname'],
            db_table=config['db_stop_table'],
            lat_small=config['lat_small'],
            lat_big=config['lat_big'],
            lon_small=config['lon_small'],
            lon_big=config['lon_big']
        )
        cursor.execute(check_stops_query)
        result_stops = cursor.fetchall()

        for db_stop_id, db_stop_lat, db_stop_lon, db_stop_name, db_stop_img in result_stops:
            if db_stop_name == 'unknown' or db_stop_img == None or db_stop_name == None:
                exist_portal_query = QUERY_EXIST.format(
                    db_name=config['db_portal_name'],
                    db_img=config['db_portal_img'],
                    db_dbname=config['db_portal_dbname'],
                    db_table=config['db_portal_table'],
                    db_lat=config['db_portal_lat'],
                    db_lon=config['db_portal_lon'],
                    lat=db_stop_lat,
                    lon=db_stop_lon
                )
                cursor.execute(exist_portal_query)
                result_portals = cursor.fetchall()

                print("updating stop", result_portals[0][0])

                update_stop_query = QUERY_UPDATE.format(
                    db_dbname=config['db_dbname'],
                    db_table=config['db_stop_table'],
                    db_name=config['db_stop_name'],
                    db_img=config['db_stop_img'],
                    img=result_portals[0][1],
                    name=result_portals[0][0],
                    db_id=config['db_stop_id'],
                    id=db_stop_id
                )
                cursor.execute(update_stop_query)

def check_stops(cursor, config):
    if config['send_stops']:
        print("Checking for new stops")
        check_stops_query = QUERY_CHECK.format(
            db_id=config['db_stop_id'],
            db_lat=config['db_stop_lat'],
            db_lon=config['db_stop_lon'],
            db_name=config['db_stop_name'],
            db_img=config['db_stop_img'],
            db_dbname=config['db_dbname'],
            db_table=config['db_stop_table'],
            lat_small=config['lat_small'],
            lat_big=config['lat_big'],
            lon_small=config['lon_small'],
            lon_big=config['lon_big']
        )
        cursor.execute(check_stops_query)
        result_stops = cursor.fetchall()

        for db_stop_id, db_stop_lat, db_stop_lon, db_stop_name, db_stop_img in result_stops:
            if db_stop_img == None:
                if not db_stop_id in get_stops_unfull():

                    print("sending unfull stop: ", db_stop_id)
                    send_webhook_stop_unfull(db_stop_id, db_stop_lat, db_stop_lon, config)
                    time.sleep(1)
            else:
                if not db_stop_id in get_stops_full():
                    print("sending full stop: ", db_stop_name)
                    send_webhook_stop_full(db_stop_id, db_stop_lat, db_stop_lon, db_stop_name, db_stop_img, config)
                    time.sleep(1)

def update_gyms(cursor, config):
    if config['update_gym_portal'] or config['update_gym_stop']:
        if config['db_scan_schema'] == "mad":
            check_gyms_query = QUERY_CHECK_GYMS_MAD.format(
                db_gym_id=config['db_gym_id'],
                db_gym_lat=config['db_gym_lat'],
                db_gym_lon=config['db_gym_lon'],
                db_gym_name=config['db_gym_name'],
                db_gym_img=config['db_gym_img'],
                db_dbname=config['db_dbname'],
                db_gym_table=config['db_gym_table'],
                db_gymdetails_table=config['db_gymdetails_table'],
                lat_small=config['lat_small'],
                lat_big=config['lat_big'],
                lon_small=config['lon_small'],
                lon_big=config['lon_big']
            )
        else:
            check_gym_query = QUERY_CHECK.format(
                db_id=config['db_gym_id'],
                db_lat=config['db_gym_lat'],
                db_lon=config['db_gym_lon'],
                db_name=config['db_gym_name'],
                db_img=config['db_gym_img'],
                db_dbname=config['db_dbname'],
                db_table=config['db_gym_table'],
                lat_small=config['lat_small'],
                lat_big=config['lat_big'],
                lon_small=config['lon_small'],
                lon_big=config['lon_big']
            )  
        cursor.execute(check_gyms_query)
        result_gyms = cursor.fetchall()

        if config['update_gym_portal']:
            print("Checking if a gym can be updated through portal info")
            for db_gym_id, db_gym_lat, db_gym_lon, db_gym_name, db_gym_img in result_gyms:
                if db_gym_name == 'unknown' or db_gym_img == None or db_gym_name == None:
                    exist_portal_query = QUERY_EXIST.format(
                        db_name=config['db_portal_name'],
                        db_img=config['db_portal_img'],
                        db_dbname=config['db_portal_dbname'],
                        db_table=config['db_portal_table'],
                        db_lat=config['db_portal_lat'],
                        db_lon=config['db_portal_lon'],
                        lat=db_gym_lat,
                        lon=db_gym_lon
                    )
                    cursor.execute(exist_portal_query)
                    result_portals = cursor.fetchall()

                    print("updating gym", result_portals[0][0], "with portal info")

                    update_gym_query = QUERY_UPDATE.format(
                        db_dbname=config['db_dbname'],
                        db_table=config['db_gymdetails_table'],
                        db_name=config['db_gym_name'],
                        db_img=config['db_gym_img'],
                        img=result_portals[0][1],
                        name=result_portals[0][0],
                        db_id=config['db_gym_id'],
                        id=db_gym_id
                    )
                    cursor.execute(update_gym_query)

                    if config['delete_stops']:
                        print("Deleting converted stop")
                        delete_stop_query = QUERY_DELETE_STOP.format(
                            db_dbname=config['db_dbname'],
                            db_stop_table=config['db_stop_table'],
                            db_stop_lat=config['db_stop_lat'],
                            db_stop_lon=config['db_stop_lon'],
                            lat=db_gym_lat,
                            lon=db_gym_lon
                        )
                        cursor.execute(delete_stop_query)

        if config['update_gym_stop']:
            print("Checking if a gym can be updated through stop info")
            for db_gym_id, db_gym_lat, db_gym_lon, db_gym_name, db_gym_img in result_gyms:
                if db_gym_name == 'unknown' or db_gym_img == None or db_gym_name == None:
                    exist_stop_query = QUERY_EXIST.format(
                        db_name=config['db_stop_name'],
                        db_img=config['db_stop_img'],
                        db_dbname=config['db_dbname'],
                        db_table=config['db_stop_table'],
                        db_lat=config['db_stop_lat'],
                        db_lon=config['db_stop_lon'],
                        lat=db_gym_lat,
                        lon=db_gym_lon
                    )
                    cursor.execute(exist_stop_query)
                    result_stops = cursor.fetchall()

                    print("updating gym", result_stops[0][0], "with portal info")

                    update_gym_query = QUERY_UPDATE.format(
                        db_dbname=config['db_dbname'],
                        db_table=config['db_gymdetails_table'],
                        db_name=config['db_gym_name'],
                        db_img=config['db_gym_img'],
                        img=result_stops[0][1],
                        name=result_stops[0][0],
                        db_id=config['db_gym_id'],
                        id=db_gym_id
                    )
                    cursor.execute(update_gym_query)

                    if config['delete_stops']:
                        print("Deleting converted stop")
                        delete_stop_query = QUERY_DELETE_STOP.format(
                            db_dbname=config['db_dbname'],
                            db_stop_table=config['db_stop_table'],
                            db_stop_lat=config['db_stop_lat'],
                            db_stop_lon=config['db_stop_lon'],
                            lat=db_gym_lat,
                            lon=db_gym_lon
                        )
                        cursor.execute(delete_stop_query)

def check_gyms(cursor, config):
    if config['send_gyms']:
        print("Checking for new gyms")
        if config['db_scan_schema'] == "mad":
            check_gyms_query = QUERY_CHECK_GYMS_MAD.format(
                db_gym_id=config['db_gym_id'],
                db_gym_lat=config['db_gym_lat'],
                db_gym_lon=config['db_gym_lon'],
                db_gym_name=config['db_gym_name'],
                db_gym_img=config['db_gym_img'],
                db_dbname=config['db_dbname'],
                db_gym_table=config['db_gym_table'],
                db_gymdetails_table=config['db_gymdetails_table'],
                lat_small=config['lat_small'],
                lat_big=config['lat_big'],
                lon_small=config['lon_small'],
                lon_big=config['lon_big']
            )
        else:
            check_gym_query = QUERY_CHECK.format(
                db_id=config['db_gym_id'],
                db_lat=config['db_gym_lat'],
                db_lon=config['db_gym_lon'],
                db_name=config['db_gym_name'],
                db_img=config['db_gym_img'],
                db_dbname=config['db_dbname'],
                db_table=config['db_gym_table'],
                lat_small=config['lat_small'],
                lat_big=config['lat_big'],
                lon_small=config['lon_small'],
                lon_big=config['lon_big']
            )  
        cursor.execute(check_gyms_query)
        result_gyms = cursor.fetchall()

        for db_gym_id, db_gym_lat, db_gym_lon, db_gym_name, db_gym_img in result_gyms:
            if db_gym_name == 'unknown' or db_gym_img == None or db_gym_name == None:
                if not db_gym_id in get_gyms_unfull():

                    print("sending unfull gym: ", db_gym_id)
                    send_webhook_gym_unfull(db_gym_id, db_gym_lat, db_gym_lon, config)
                    time.sleep(1)
            else:
                if not db_gym_id in get_gyms_full():
                    print("sending full gym: ", db_gym_name)
                    send_webhook_gym_full(db_gym_id, db_gym_lat, db_gym_lon, db_gym_name, db_gym_img, config)
                    time.sleep(1)

def main():
    print("-------------------------------")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="default.ini", help="Config file to use")
    args = parser.parse_args()
    config_path = args.config
    config = create_config(config_path)

    cursor = connect_db(config)
    db_config(config)

    check_portals(cursor, config)
    update_stop_portal(cursor, config)
    check_stops(cursor, config)
    update_gyms(cursor, config)
    check_gyms(cursor, config)

    cursor.close()
    print("-------------------------------")
    if config['dosleep']:
        print("Loop done. Waiting", config['sleeptime'], "seconds")
        time.sleep(config['sleeptime'])

while True:
    main()
    """if config['dosleep']:
        print("Loop done. Waiting", config['sleeptime'])
        time.sleep(config['sleeptime'])"""