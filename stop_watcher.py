# -*- coding: utf-8 -*-

import time
import json
import requests
import argparse
import pyimgur
import geocoder
import sys

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
QUERY_INIT = """SELECT {db_id} FROM {db_dbname}.{db_table}"""
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
QUERY_SF = """(SELECT {db_lat}, {db_lon},
  "stop" AS type,
  POW(69.1 * ({db_lat} - {sf_lat}), 2) + POW(69.1 * ({sf_lon} - {db_lon}) * COS({db_lat} / 57.3), 2) AS distance
  FROM {db_dbname}.{db_table_1}
  WHERE {db_lat} != {sf_lat} AND {db_lon} != {sf_lon})
UNION
  (SELECT {db_lat}, {db_lon},
  "gym" AS type,
  POW(69.1 * ({db_lat} - {sf_lat}), 2) + POW(69.1 * ({sf_lon} - {db_lon}) * COS({db_lat} / 57.3), 2) AS distance
  FROM {db_dbname}.{db_table_2}
  WHERE {db_lat} != {sf_lat} AND {db_lon} != {sf_lon})
ORDER BY distance ASC
LIMIT {limit}
"""
QUERY_SF_PORTAL = """SELECT {db_lat}, {db_lon},
  POW(69.1 * ({db_lat} - {sf_lat}), 2) + POW(69.1 * ({sf_lon} - {db_lon}) * COS({db_lat} / 57.3), 2) AS distance
FROM {db_dbname}.{db_table}
WHERE {db_lat} != {sf_lat} AND {db_lon} != {sf_lon}
ORDER BY distance ASC
LIMIT {limit}
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
    config['dosleep'] = config_raw.getboolean(
        'Config',
        'LOOP')
    config['sleeptime'] = config_raw.getint(
        'Config',
        'SECONDS_BETWEEN_LOOPS')
    config['bbox'] = config_raw.get(
        'Config',
        'BBOX')
    config['bbox'] = list(config['bbox'].split(','))
    config['language'] = config_raw.get(
        'Config',
        'LANGUAGE')

    ### Discord
    config['webhook_url_stop'] = config_raw.get(
        'Discord',
        'STOP_WEBHOOK')
    config['webhook_url_gym'] = config_raw.get(
        'Discord',
        'GYM_WEBHOOK')
    config['webhook_url_portal'] = config_raw.get(
        'Discord',
        'PORTAL_WEBHOOK')
    config['stop_img'] = config_raw.get(
        'Discord',
        'STOP_IMAGE')
    config['embed_stop_color'] = config_raw.getint(
        'Discord',
        'STOP_COLOR')
    config['gym_img'] = config_raw.get(
        'Discord',
        'GYM_IMAGE')
    config['embed_gym_color'] = config_raw.getint(
        'Discord',
        'GYM_COLOR')
    config['portal_img'] = config_raw.get(
        'Discord',
        'PORTAL_IMAGE')
    config['embed_portal_color'] = config_raw.getint(
        'Discord',
        'PORTAL_COLOR')

    ### Static Map
    config['static_provider'] = config_raw.get(
        'Static Map',
        'PROVIDER')
    config['imgur_all'] = config_raw.getboolean(
        'Static Map',
        'USE_IMGUR_MIRRORS_FOR_EVERYTHING')
    config['static_fancy'] = config_raw.getboolean(
        'Static Map',
        'SUPER_FANCY_STATIC_MAPS')
    config['client_id_imgur'] = config_raw.get(
        'Static Map',
        'IMGUR_CLIENT_ID')
    config['marker_limit'] = config_raw.getint(
        'Static Map',
        'MARKER_LIMIT')
    config['static_key'] = config_raw.get(
        'Static Map',
        'KEY')
    config['static_zoom'] = config_raw.getint(
        'Static Map',
        'ZOOM')
    config['static_width'] = config_raw.getint(
        'Static Map',
        'WIDTH')
    config['static_height'] = config_raw.getint(
        'Static Map',
        'HEIGHT')
    config['static_marker_size'] = config_raw.getint(
        'Static Map',
        'MARKER_SIZE')
    config['static_marker_color_stop'] = config_raw.get(
        'Static Map',
        'MARKER_COLOR_STOP')
    config['static_marker_color_gym'] = config_raw.get(
        'Static Map',
        'MARKER_COLOR_GYM')
    config['static_marker_color_portal'] = config_raw.get(
        'Static Map',
        'MARKER_COLOR_PORTAL')
    config['static_selfhosted_url'] = config_raw.get(
        'Static Map',
        'TILESERVER_URL')
    config['geocoding'] = config_raw.getboolean(
        'Static Map',
        'USE_GEOCODING')

    ### DATABASE
    config['db_scan_schema'] = config_raw.get(
        'DB',
        'SCANNER_DB_SCHEMA')
    config['db_portal_schema'] = config_raw.get(
        'DB',
        'PORTAL_DB_SCHEMA')
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
        'SCANNER_DB_NAME')

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
        config['db_gymdetails_table'] = "gym"
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

    if config['static_marker_size'] == 0:
        if config['static_provider'] == "google":
            config['static_marker_size'] = "tiny"
        elif config['static_provider'] == "osm":
            print("Please choose a marker size between 1 and 3")
    elif config['static_marker_size'] == 1:
        if config['static_provider'] == "google":
            config['static_marker_size'] = "small"
        elif config['static_provider'] == "osm":
            config['static_marker_size'] = "sm"
    elif config['static_marker_size'] == 2:
        if config['static_provider'] == "google":
            config['static_marker_size'] = "mid"
        elif config['static_provider'] == "osm":
            config['static_marker_size'] = "md"
    elif config['static_marker_size'] == 3:
        if config['static_provider'] == "google":
            config['static_marker_size'] = "normal"
        elif config['static_provider'] == "osm":
            config['static_marker_size'] = "lg"
    else:
        print("Please choose another marker size.")

    return config

def connect_db(config):
    mydb = connect(
        host=config['db_host'],
        user=config['db_user'],
        passwd=config['db_pass'],
        database=config['db_dbname'],
        port=config['db_port'],
        autocommit=True)

    return mydb

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

def write_portals(cursor, config):
    if config['send_portals']:
        print("Checking for portals to write")
        check_portals_query = QUERY_INIT.format(
            db_id=config['db_portal_id'],
            db_dbname=config['db_portal_dbname'],
            db_table=config['db_portal_table']
        )
        cursor.execute(check_portals_query)
        portals = cursor.fetchall()

        for db_id in portals:
            for var in db_id:
                if not var in get_portals():
                    print("Writing portal id", var)
                    with open("txt/portals.txt", "a") as f:
                        f.write(var + "\n")

def write_stops(cursor, config):
    if config['send_stops']:
        print("Checking for stops to write")
        check_stops_query = QUERY_INIT.format(
            db_id=config['db_stop_id'],
            db_dbname=config['db_dbname'],
            db_table=config['db_stop_table']
        )
        cursor.execute(check_stops_query)
        stops = cursor.fetchall()

        for db_id in stops:
            for var in db_id:
                if not var in get_stops_full():
                    print("Writing full stop id", var)
                    with open("txt/stop_full.txt", "a") as f:
                        f.write(var + "\n")
        for db_id in stops:
            for var in db_id:
                if not var in get_stops_unfull():
                    print("Writing unfull stop id", var)
                    with open("txt/stop_unfull.txt", "a") as f:
                        f.write(var + "\n")

def write_gyms(cursor, config):
    if config['send_gyms']:
        print("Checking for gyms to write")
        check_gyms_query = QUERY_INIT.format(
            db_id=config['db_gym_id'],
            db_dbname=config['db_dbname'],
            db_table=config['db_gym_table']
        )
        cursor.execute(check_gyms_query)
        gyms = cursor.fetchall()

        for db_id in gyms:
            for var in db_id:
                if not var in get_gyms_full():
                    print("Writing full gym id", var)
                    with open("txt/gym_full.txt", "a") as f:
                        f.write(var + "\n")
        for db_id in gyms:
            for var in db_id:
                if not var in get_gyms_unfull():
                    print("Writing unfull gym id", var)
                    with open("txt/gym_unfull.txt", "a") as f:
                        f.write(var + "\n")

def imgur(static_map, config):
    im = pyimgur.Imgur(config['client_id_imgur'])
    uploaded_image = im.upload_image(url=static_map)
    static_map = (uploaded_image.link)
    return static_map

def generate_static_map(poitype, lat, lon, config):
    if config['static_provider'] == "google":
        static_map = ("https://maps.googleapis.com/maps/api/staticmap?center=" + str(lat) + "," + str(lon) + "&zoom=" + str(config['static_zoom']) + "&scale=1&size=" + str(config['static_width']) + "x" + str(config['static_height']) + "&maptype=roadmap&key=" + config['static_key'] + "&format=png&visual_refresh=true&markers=size:" + config['static_marker_size'] + "%7Ccolor:0x" + config['static_marker_color_stop'] + "%7Clabel:%7C" + str(lat) + "," + str(lon))
    elif config['static_provider'] == "osm":
        static_map = ("https://www.mapquestapi.com/staticmap/v5/map?locations=" + str(lat) + "," + str(lon) + "&size=" + str(config['static_width']) + "," + str(config['static_height']) + "&defaultMarker=marker-" + str(config['static_marker_size']) + "-" + config['static_marker_color_stop'] + "&zoom=" + str(config['static_zoom']) + "&key=" + config['static_key'])
    elif config['static_provider'] == "tileserver-gl":
        static_map = (config['static_selfhosted_url'] + "static/klokantech-basic/" + str(lat) + "/" + str(lon) + "/" + str(config['static_zoom']) + "/" + str(config['static_width']) + "/" + str(config['static_height']) + "/1/png?markers=%5B%7B%22url%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png%22%2C%22height%22%3A128%2C%22width%22%3A128%2C%22x_offset%22%3A0%2C%22y_offset%22%3A0%2C%22latitude%22%3A%20" + str(lat) + "%2C%22longitude%22%3A%20" + str(lon) + "%7D%5D")    
    elif config['static_provider'] == "mapbox":
        if config['static_fancy']:
            static_map = "https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/"

            marker_limit = config['marker_limit'] - 1

            if poitype == "portal":
                sf_query_portal = QUERY_SF_PORTAL.format(
                    db_dbname=config['db_portal_dbname'],
                    db_table=config['db_portal_table'],
                    db_lat=config['db_portal_lat'],
                    db_lon=config['db_portal_lon'],
                    sf_lat=lat,
                    sf_lon=lon,
                    limit=marker_limit
                )
                cursor.execute(sf_query_portal)
                sf_portals = cursor.fetchall()

                for db_portal_lat, db_portal_lon, distance in sf_portals:
                    static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fportal_gray.png(" + str(db_portal_lon) + "," + str(db_portal_lat) + "),")
    
            else:
                sf_query = QUERY_SF.format(
                    db_dbname=config['db_dbname'],
                    db_table_1=config['db_stop_table'],
                    db_table_2=config['db_gym_table'],
                    db_lat=config['db_stop_lat'],
                    db_lon=config['db_stop_lon'],
                    sf_lat=lat,
                    sf_lon=lon,
                    limit=marker_limit
                )
                cursor.execute(sf_query)
                results_sf = cursor.fetchall()

                for db_stop_lat, db_stop_lon, type, distance in results_sf:
                    static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2F" + type + "_gray.png(" + str(db_stop_lon) + "," + str(db_stop_lat) + "),")

            static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2F" + poitype + "_normal.png(" + str(lon) + "," + str(lat) + ")/" + str(lon) + "," + str(lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
            static_map = imgur(static_map, config)
        else:
            static_map = ("https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2F" + (poitype) + "_normal.png(" + str(lon) + "," + str(lat) + ")/" + str(lon) + "," + str(lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
    else:
        static_map = ""  

    if config['imgur_all'] and not config['static_fancy']:
        static_map = imgur(static_map, config)

    return static_map

def generate_text(lat, lon, config):
    text = ("[Google Maps](https://www.google.com/maps/search/?api=1&query=" + str(lat) + "," + str(lon) + ")")

    if config['geocoding']:
        if config['static_provider'] == "google":
            geocode = geocoder.google([db_poi_lat, db_poi_lon], method='reverse', key=config['static_key'], language=config['language'])
        elif config['static_provider'] == "osm":
            geocode = geocoder.mapquest([db_poi_lat, db_poi_lon], method='reverse', key=config['static_key'], language=config['language'])
        elif config['static_provider'] == "mapbox":
            geocode = geocoder.mapbox([db_poi_lat, db_poi_lon], method='reverse', key=config['static_key'], language=config['language'])
        else:
            address = ""  

        text = (text + "\n" + geocode.address)

    return text

def send_webhook_full(lat, lon, type, username, avatar, color, name, image, webhook, config):
    static_map = generate_static_map(type, lat, lon, config)
    text = generate_text(lat, lon, config)
    if type == "portal":
        text = text + " | [Intel](https://intel.ingress.com/intel?ll=" + str(lat) + "," + str(lon) + "&z=18)"

    data = {
        "username": username,
        "avatar_url": avatar,
        "embeds": [{
            "title": name,
            "description": text,
            "color": color,
            "thumbnail": {
                "url": image
            },
            "image": {
                "url": static_map
            }
        }]
    }
    webhooks = json.loads(webhook)
    for webhook in webhooks:
        result = requests.post(webhook, json=data)
        print(result)

def send_webhook_unfull(lat, lon, type, username, avatar, color, webhook, config):
    static_map = generate_static_map(type, lat, lon, config)
    text = generate_text(lat, lon, config)

    data = {
        "username": username,
        "avatar_url": avatar,
        "embeds": [{
            "description": text,
            "color": color,
            "image": {
                "url": static_map
            }
        }]
    }
    webhooks = json.loads(webhook)
    for webhook in webhooks:
        result = requests.post(webhook, json=data)
        print(result)

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
            lat_small=config['bbox'][1],
            lat_big=config['bbox'][3],
            lon_small=config['bbox'][0],
            lon_big=config['bbox'][2]
        )
        cursor.execute(check_portals_query)
        result_portals = cursor.fetchall()

        for db_portal_id, db_portal_lat, db_portal_lon, db_portal_name, db_portal_img in result_portals:
            if not db_portal_id in get_portals():
                print("sending portal: ", db_portal_name)
                send_webhook_full(db_portal_lat, db_portal_lon, "portal", locale['portal_title'], config['portal_img'], config['embed_portal_color'], db_portal_name, db_portal_img, config["webhook_url_portal"], config)
                with open("txt/portals.txt", "a") as f:
                    f.write(db_portal_id + "\n")
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
            lat_small=config['bbox'][1],
            lat_big=config['bbox'][3],
            lon_small=config['bbox'][0],
            lon_big=config['bbox'][2]
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

                for db_portal_name, db_portal_img in result_portals:
                    if db_portal_name == None or db_portal_img == None:
                        print("Tried to update Stop at", db_stop_lat, ",", db_stop_lon, "but Portal has no image or name. Check your DB!")
                    else:
                        print("updating stop", db_portal_name)
                        db_portal_name = db_portal_name.replace("'", "\\'")
                        update_stop_query = QUERY_UPDATE.format(
                            db_dbname=config['db_dbname'],
                            db_table=config['db_stop_table'],
                            db_name=config['db_stop_name'],
                            db_img=config['db_stop_img'],
                            img=db_portal_img,
                            name=db_portal_name,
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
            lat_small=config['bbox'][1],
            lat_big=config['bbox'][3],
            lon_small=config['bbox'][0],
            lon_big=config['bbox'][2]
        )
        cursor.execute(check_stops_query)
        result_stops = cursor.fetchall()

        for db_stop_id, db_stop_lat, db_stop_lon, db_stop_name, db_stop_img in result_stops:
            if db_stop_img == None:
                if not db_stop_id in get_stops_unfull():

                    print("sending unfull stop: ", db_stop_id)
                    send_webhook_unfull(db_stop_lat, db_stop_lon, "stop", locale['unfull_stop_title'], config['stop_img'], config['embed_stop_color'], config["webhook_url_stop"], config)
                    with open("txt/stop_unfull.txt", "a") as f:
                        f.write(db_stop_id + "\n")
                    time.sleep(1)
            else:
                if not db_stop_id in get_stops_full():
                    print("sending full stop: ", db_stop_name)
                    send_webhook_full(db_stop_lat, db_stop_lon, "stop", locale['full_stop_title'], config['stop_img'], config['embed_stop_color'], db_stop_name, db_stop_img, config["webhook_url_stop"], config)
                    with open("txt/stop_full.txt", "a") as f:
                        f.write(db_stop_id + "\n")
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
                lat_small=config['bbox'][1],
                lat_big=config['bbox'][3],
                lon_small=config['bbox'][0],
                lon_big=config['bbox'][2]
            )
        else:
            check_gyms_query = QUERY_CHECK.format(
                db_id=config['db_gym_id'],
                db_lat=config['db_gym_lat'],
                db_lon=config['db_gym_lon'],
                db_name=config['db_gym_name'],
                db_img=config['db_gym_img'],
                db_dbname=config['db_dbname'],
                db_table=config['db_gym_table'],
                lat_small=config['bbox'][1],
                lat_big=config['bbox'][3],
                lon_small=config['bbox'][0],
                lon_big=config['bbox'][2]
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

                    for db_portal_name, db_portal_img in result_portals:
                        if db_portal_name == None or db_portal_img == None:
                            print("Tried to update Gym at", db_gym_lat, ",", db_gym_lon, "using Portal info, but Portal has no image or name. Check your DB!")
                        else:
                            print("updating gym", db_portal_name, "with portal info")
                            db_portal_name = db_portal_name.replace("'", "\\'")
                            update_gym_query = QUERY_UPDATE.format(
                                db_dbname=config['db_dbname'],
                                db_table=config['db_gymdetails_table'],
                                db_name=config['db_gym_name'],
                                db_img=config['db_gym_img'],
                                img=db_portal_img,
                                name=db_portal_name,
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

                    for db_stop_name, db_stop_img in result_stops:
                        if db_stop_name == None or db_stop_img == None:
                            print("Tried to update Gym at", db_gym_lat, ",", db_gym_lon, "using Stop info, but Stop has no image or name. Check your DB!")
                        else:
                            print("updating gym", db_stop_name, "with stop info")
                            db_stop_name = db_stop_name.replace("'", "\\'")
                            update_gym_query = QUERY_UPDATE.format(
                                db_dbname=config['db_dbname'],
                                db_table=config['db_gymdetails_table'],
                                db_name=config['db_gym_name'],
                                db_img=config['db_gym_img'],
                                img=db_stop_img,
                                name=db_stop_name,
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
                lat_small=config['bbox'][1],
                lat_big=config['bbox'][3],
                lon_small=config['bbox'][0],
                lon_big=config['bbox'][2]
            )
        else:
            check_gyms_query = QUERY_CHECK.format(
                db_id=config['db_gym_id'],
                db_lat=config['db_gym_lat'],
                db_lon=config['db_gym_lon'],
                db_name=config['db_gym_name'],
                db_img=config['db_gym_img'],
                db_dbname=config['db_dbname'],
                db_table=config['db_gym_table'],
                lat_small=config['bbox'][1],
                lat_big=config['bbox'][3],
                lon_small=config['bbox'][0],
                lon_big=config['bbox'][2]
            )  
        cursor.execute(check_gyms_query)
        result_gyms = cursor.fetchall()

        for db_gym_id, db_gym_lat, db_gym_lon, db_gym_name, db_gym_img in result_gyms:
            if db_gym_name == 'unknown' or db_gym_img == None or db_gym_name == None:
                if not db_gym_id in get_gyms_unfull():
                    print("sending unfull gym: ", db_gym_id)
                    send_webhook_unfull(db_gym_lat, db_gym_lon, "gym", locale['unfull_gym_title'], config['gym_img'], config['embed_gym_color'], config["webhook_url_gym"], config)
                    with open("txt/gym_unfull.txt", "a") as f:
                        f.write(db_gym_id + "\n")
                    time.sleep(1)
            else:
                if not db_gym_id in get_gyms_full():
                    print("sending full gym: ", db_gym_name)
                    send_webhook_full(db_gym_lat, db_gym_lon, "gym", locale['full_gym_title'], config['gym_img'], config['embed_gym_color'], db_gym_name, db_gym_img, config["webhook_url_gym"], config)
                    with open("txt/gym_full.txt", "a") as f:
                        f.write(db_gym_id + "\n")
                    time.sleep(1)

def main():
    print("-------------------------------")
    global cursor
    mydb = connect_db(config)
    cursor = mydb.cursor()

    check_portals(cursor, config)
    update_stop_portal(cursor, config)
    check_stops(cursor, config)
    update_gyms(cursor, config)
    check_gyms(cursor, config)

    cursor.close()
    mydb.close()
    print("-------------------------------")

if __name__ == "__main__":
    print("-------------------------------")
    print("First run! Checking if your txt files are empty...")
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="default.ini", help="Config file to use")
    parser.add_argument("-i", "--init", action='store_true', help="Copy every missing Stop/Gym/Portal ID into Stop Watcher's txt files")
    args = parser.parse_args()
    config_path = args.config
    config = create_config(config_path)

    mydb = connect_db(config)
    cursor = mydb.cursor()

    if args.init:
        write_portals(cursor, config)
        write_stops(cursor, config)
        write_gyms(cursor, config)
        print("Succesfully copied all missing IDs into the txt files.")
        sys.exit()

    with open(f"locale/{config['language']}.json") as localejson:
        locale = json.load(localejson)

    if not get_portals():
        write_portals(cursor, config)
        print("Found an empty portals.txt file - Ran init.py on portals.")
    if not get_stops_unfull() or not get_stops_full():
        write_stops(cursor, config)
        print("Found an empty stops.txt file - Ran init.py on stops.")
    if not get_gyms_unfull() or not get_gyms_full():
        write_gyms(cursor, config)
        print("Found an empty gyms.txt file - Ran init.py on gyms.")
    
    cursor.close()
    mydb.close()

    while config['dosleep']:
        main()
        print("Loop done. Waiting", config['sleeptime'], "seconds")
        time.sleep(config['sleeptime'])
    else:
        main()
        print("Looping disabled - Stopping gracefully.")
