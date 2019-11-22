# -*- coding: utf-8 -*-

import time
import requests
import argparse
import init
import pyimgur

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
QUERY_SF = """SELECT {db_lat}, {db_lon} FROM {db_dbname}.{db_table}
WHERE (
    {db_lon} != {sf_lon} AND {db_lat} != {sf_lat}
  AND
    {db_lat} >= {lat_small} AND {db_lat} <= {lat_big}
  AND
    {db_lon} >= {lon_small} AND {db_lon} <= {lon_big}
)
ORDER BY {db_lat} DESC
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
    config['embed_stop_color'] = config_raw.getint(
        'Embeds',
        'STOP_COLOR')
    config['gym_img'] = config_raw.get(
        'Embeds',
        'GYM_IMAGE')
    config['gym_full_username'] = config_raw.get(
        'Embeds',
        'GYM_DETAILS_USERNAME')
    config['gym_unfull_username'] = config_raw.get(
        'Embeds',
        'GYM_NO_DETAILS_USERNAME')
    config['embed_gym_color'] = config_raw.getint(
        'Embeds',
        'GYM_COLOR')
    config['portal_img'] = config_raw.get(
        'Embeds',
        'PORTAL_IMAGE')
    config['portal_username'] = config_raw.get(
        'Embeds',
        'PORTAL_USERNAME')
    config['embed_portal_color'] = config_raw.getint(
        'Embeds',
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

def static_config(config):
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

def superfancystaticmap(db_poi_lat, db_poi_lon, config):
    sf_lat_min = db_poi_lat - 0.002000
    sf_lat_max = db_poi_lat + 0.002000
    sf_lon_min = db_poi_lon - 0.003000
    sf_lon_max = db_poi_lon + 0.003000

    static_map = "https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/"

    sf_query_stop = QUERY_SF.format(
        db_dbname=config['db_dbname'],
        db_table=config['db_stop_table'],
        db_lat=config['db_stop_lat'],
        db_lon=config['db_stop_lon'],
        lat_small=sf_lat_min,
        lat_big=sf_lat_max,
        lon_small=sf_lon_min,
        lon_big=sf_lon_max,
        sf_lat=db_poi_lat,
        sf_lon=db_poi_lon
    )
    cursor.execute(sf_query_stop)
    sf_stops = cursor.fetchall()

    for db_stop_lat, db_stop_lon in sf_stops:
        static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_gray.png(" + str(db_stop_lon) + "," + str(db_stop_lat) + "),")

    sf_query_gym = QUERY_SF.format(
        db_dbname=config['db_dbname'],
        db_table=config['db_gym_table'],
        db_lat=config['db_gym_lat'],
        db_lon=config['db_gym_lon'],
        lat_small=sf_lat_min,
        lat_big=sf_lat_max,
        lon_small=sf_lon_min,
        lon_big=sf_lon_max,
        sf_lat=db_poi_lat,
        sf_lon=db_poi_lon
    )
    cursor.execute(sf_query_gym)
    sf_gyms = cursor.fetchall()

    for db_gym_lat, db_gym_lon in sf_gyms:
        static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fgym_gray.png(" + str(db_gym_lon) + "," + str(db_gym_lat) + "),")

    return static_map

def imgur(static_map, config):
    im = pyimgur.Imgur(config['client_id_imgur'])
    uploaded_image = im.upload_image(url=static_map)
    static_map = (uploaded_image.link)
    return static_map

def send_webhook_portal(db_portal_id, db_portal_lat, db_portal_lon, db_portal_name, db_portal_img, config):
    db_poi_lat = db_portal_lat
    db_poi_lon = db_portal_lon
    navigation = ("[Google Maps](https://www.google.com/maps/search/?api=1&query=" + str(db_poi_lat) + "," + str(db_poi_lon) + ") | [Intel](https://intel.ingress.com/intel?ll=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&z=15&pll=" + str(db_poi_lat) + "," + str(db_poi_lon) + ")")

    if config['static_provider'] == "google":
        static_map = ("https://maps.googleapis.com/maps/api/staticmap?center=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&zoom=" + str(config['static_zoom']) + "&scale=1&size=" + str(config['static_width']) + "x" + str(config['static_height']) + "&maptype=roadmap&key=" + config['static_key'] + "&format=png&visual_refresh=true&markers=size:" + config['static_marker_size'] + "%7Ccolor:0x" + config['static_marker_color_portal'] + "%7Clabel:%7C" + str(db_poi_lat) + "," + str(db_poi_lon))
    elif config['static_provider'] == "osm":
        static_map = ("https://www.mapquestapi.com/staticmap/v5/map?locations=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&size=" + str(config['static_width']) + "," + str(config['static_height']) + "&defaultMarker=marker-" + str(config['static_marker_size']) + "-" + config['static_marker_color_portal'] + "&zoom=" + str(config['static_zoom']) + "&key=" + config['static_key'])
    elif config['static_provider'] == "tileserver-gl":
        static_map = (config['static_selfhosted_url'] + "static/klokantech-basic/" + str(db_poi_lat) + "/" + str(db_poi_lon) + "/" + str(config['static_zoom']) + "/" + str(config['static_width']) + "/" + str(config['static_height']) + "/1/png?markers=%5B%7B%22url%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png%22%2C%22height%22%3A128%2C%22width%22%3A128%2C%22x_offset%22%3A0%2C%22y_offset%22%3A0%2C%22latitude%22%3A%20" + str(db_poi_lat) + "%2C%22longitude%22%3A%20" + str(db_poi_lon) + "%7D%5D")
    elif config['static_provider'] == "mapbox":
        if config['static_fancy']:
            sf_lat_min = db_poi_lat - 0.002000
            sf_lat_max = db_poi_lat + 0.002000
            sf_lon_min = db_poi_lon - 0.003000
            sf_lon_max = db_poi_lon + 0.003000

            static_map = "https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/"

            sf_query_portal = QUERY_SF.format(
                db_dbname=config['db_portal_dbname'],
                db_table=config['db_portal_table'],
                db_lat=config['db_portal_lat'],
                db_lon=config['db_portal_lon'],
                lat_small=sf_lat_min,
                lat_big=sf_lat_max,
                lon_small=sf_lon_min,
                lon_big=sf_lon_max,
                sf_lat=db_poi_lat,
                sf_lon=db_poi_lon
            )
            cursor.execute(sf_query_portal)
            sf_portals = cursor.fetchall()

            for db_portal_lat, db_portal_lon in sf_portals:
                static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fportal_gray.png(" + str(db_portal_lon) + "," + str(db_portal_lat) + "),")
 
            static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fportal_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
            static_map = imgur(static_map, config)

        else:
            static_map = ("https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fportal_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
    else:
        static_map = ""  

    if config['imgur_all'] and not config['static_fancy']:
        static_map = imgur(static_map, config)

    data = {
        "username": config['portal_username'],
        "avatar_url": config['portal_img'],
        "embeds": [{
            "color": config['embed_portal_color'],
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
    result = requests.post(config['webhook_url_portal'], json=data)
    print(result)

    with open("txt/portals.txt", "a") as f:
        f.write(db_portal_id + "\n")

def send_webhook_stop_full(db_stop_id, db_stop_lat, db_stop_lon, db_stop_name, db_stop_img, config):
    db_poi_lat = db_stop_lat
    db_poi_lon = db_stop_lon
    navigation = ("[Google Maps](https://www.google.com/maps/search/?api=1&query=" + str(db_poi_lat) + "," + str(db_poi_lon) + ")")

    if config['static_provider'] == "google":
        static_map = ("https://maps.googleapis.com/maps/api/staticmap?center=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&zoom=" + str(config['static_zoom']) + "&scale=1&size=" + str(config['static_width']) + "x" + str(config['static_height']) + "&maptype=roadmap&key=" + config['static_key'] + "&format=png&visual_refresh=true&markers=size:" + config['static_marker_size'] + "%7Ccolor:0x" + config['static_marker_color_stop'] + "%7Clabel:%7C" + str(db_poi_lat) + "," + str(db_poi_lon))
    elif config['static_provider'] == "osm":
        static_map = ("https://www.mapquestapi.com/staticmap/v5/map?locations=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&size=" + str(config['static_width']) + "," + str(config['static_height']) + "&defaultMarker=marker-" + str(config['static_marker_size']) + "-" + config['static_marker_color_stop'] + "&zoom=" + str(config['static_zoom']) + "&key=" + config['static_key'])
    elif config['static_provider'] == "tileserver-gl":
        static_map = (config['static_selfhosted_url'] + "static/klokantech-basic/" + str(db_poi_lat) + "/" + str(db_poi_lon) + "/" + str(config['static_zoom']) + "/" + str(config['static_width']) + "/" + str(config['static_height']) + "/1/png?markers=%5B%7B%22url%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png%22%2C%22height%22%3A128%2C%22width%22%3A128%2C%22x_offset%22%3A0%2C%22y_offset%22%3A0%2C%22latitude%22%3A%20" + str(db_poi_lat) + "%2C%22longitude%22%3A%20" + str(db_poi_lon) + "%7D%5D")    
    elif config['static_provider'] == "mapbox":
        if config['static_fancy']:
            static_map = superfancystaticmap(db_poi_lat, db_poi_lon, config)
            static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
            static_map = imgur(static_map, config)
        else:
            static_map = ("https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
    else:
        static_map = ""  

    if config['imgur_all'] and not config['static_fancy']:
        static_map = imgur(static_map, config)

    data = {
        "username": config['stop_full_username'],
        "avatar_url": config['stop_img'],
        "embeds": [{
            "color": config['embed_stop_color'],
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
    result = requests.post(config['webhook_url_stop'], json=data)
    print(result)

    with open("txt/stop_full.txt", "a") as f:
        f.write(db_stop_id + "\n")

def send_webhook_stop_unfull(db_stop_id, db_stop_lat, db_stop_lon, config):
    db_poi_lat = db_stop_lat
    db_poi_lon = db_stop_lon
    navigation = ("https://www.google.com/maps/search/?api=1&query=" + str(db_poi_lat) + "," + str(db_poi_lon))

    if config['static_provider'] == "google":
        static_map = ("https://maps.googleapis.com/maps/api/staticmap?center=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&zoom=" + str(config['static_zoom']) + "&scale=1&size=" + str(config['static_width']) + "x" + str(config['static_height']) + "&maptype=roadmap&key=" + config['static_key'] + "&format=png&visual_refresh=true&markers=size:" + config['static_marker_size'] + "%7Ccolor:0x" + config['static_marker_color_stop'] + "%7Clabel:%7C" + str(db_poi_lat) + "," + str(db_poi_lon))
    elif config['static_provider'] == "osm":
        static_map = ("https://www.mapquestapi.com/staticmap/v5/map?locations=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&size=" + str(config['static_width']) + "," + str(config['static_height']) + "&defaultMarker=marker-" + str(config['static_marker_size']) + "-" + config['static_marker_color_stop'] + "&zoom=" + str(config['static_zoom']) + "&key=" + config['static_key'])
    elif config['static_provider'] == "tileserver-gl":
        static_map = (config['static_selfhosted_url'] + "static/klokantech-basic/" + str(db_poi_lat) + "/" + str(db_poi_lon) + "/" + str(config['static_zoom']) + "/" + str(config['static_width']) + "/" + str(config['static_height']) + "/1/png?markers=%5B%7B%22url%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png%22%2C%22height%22%3A128%2C%22width%22%3A128%2C%22x_offset%22%3A0%2C%22y_offset%22%3A0%2C%22latitude%22%3A%20" + str(db_poi_lat) + "%2C%22longitude%22%3A%20" + str(db_poi_lon) + "%7D%5D")
    elif config['static_provider'] == "mapbox":
        if config['static_fancy']:
            static_map = superfancystaticmap(db_poi_lat, db_poi_lon, config)
            static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
            static_map = imgur(static_map, config)
        else:
            static_map = ("https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
    else:
        static_map = ""  

    if config['imgur_all'] and not config['static_fancy']:
        static_map = imgur(static_map, config)
 
    data = {
        "username": config['stop_unfull_username'],
        "avatar_url": config['stop_img'],
        "embeds": [{
            "title": "Google Maps",
            "url": navigation,
            "color": config['embed_stop_color'],
            "image": {
                "url": static_map
            }
        }]
    }
    result = requests.post(config['webhook_url_stop'], json=data)
    print(result)

    with open("txt/stop_unfull.txt", "a") as f:
        f.write(db_stop_id + "\n")

def send_webhook_gym_full(db_gym_id, db_gym_lat, db_gym_lon, db_gym_name, db_gym_img, config):
    db_poi_lat = db_gym_lat
    db_poi_lon = db_gym_lon
    navigation = ("[Google Maps](https://www.google.com/maps/search/?api=1&query=" + str(db_poi_lat) + "," + str(db_poi_lon) + ")")

    if config['static_provider'] == "google":
        static_map = ("https://maps.googleapis.com/maps/api/staticmap?center=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&zoom=" + str(config['static_zoom']) + "&scale=1&size=" + str(config['static_width']) + "x" + str(config['static_height']) + "&maptype=roadmap&key=" + config['static_key'] + "&format=png&visual_refresh=true&markers=size:" + config['static_marker_size'] + "%7Ccolor:0x" + config['static_marker_color_gym'] + "%7Clabel:%7C" + str(db_poi_lat) + "," + str(db_poi_lon))
    elif config['static_provider'] == "osm":
        static_map = ("https://www.mapquestapi.com/staticmap/v5/map?locations=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&size=" + str(config['static_width']) + "," + str(config['static_height']) + "&defaultMarker=marker-" + str(config['static_marker_size']) + "-" + config['static_marker_color_gym'] + "&zoom=" + str(config['static_zoom']) + "&key=" + config['static_key'])
    elif config['static_provider'] == "tileserver-gl":
        static_map = (config['static_selfhosted_url'] + "static/klokantech-basic/" + str(db_poi_lat) + "/" + str(db_poi_lon) + "/" + str(config['static_zoom']) + "/" + str(config['static_width']) + "/" + str(config['static_height']) + "/1/png?markers=%5B%7B%22url%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png%22%2C%22height%22%3A128%2C%22width%22%3A128%2C%22x_offset%22%3A0%2C%22y_offset%22%3A0%2C%22latitude%22%3A%20" + str(db_poi_lat) + "%2C%22longitude%22%3A%20" + str(db_poi_lon) + "%7D%5D")
    elif config['static_provider'] == "mapbox":
        if config['static_fancy']:
            static_map = superfancystaticmap(db_poi_lat, db_poi_lon, config)
            static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fgym_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
            static_map = imgur(static_map, config)
        else:
            static_map = ("https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fgym_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
    else:
        static_map = ""  
    
    if config['imgur_all'] and not config['static_fancy']:
        static_map = imgur(static_map, config)
 
    data = {
        "username": config['gym_full_username'],
        "avatar_url": config['gym_img'],
        "embeds": [{
            "color": config['embed_gym_color'],
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
    result = requests.post(config['webhook_url_gym'], json=data)
    print(result)

    with open("txt/gym_full.txt", "a") as f:
        f.write(db_gym_id + "\n")

def send_webhook_gym_unfull(db_gym_id, db_gym_lat, db_gym_lon, config):
    db_poi_lat = db_gym_lat
    db_poi_lon = db_gym_lon
    navigation = ("https://www.google.com/maps/search/?api=1&query=" + str(db_poi_lat) + "," + str(db_poi_lon))

    if config['static_provider'] == "google":
        static_map = ("https://maps.googleapis.com/maps/api/staticmap?center=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&zoom=" + str(config['static_zoom']) + "&scale=1&size=" + str(config['static_width']) + "x" + str(config['static_height']) + "&maptype=roadmap&key=" + config['static_key'] + "&format=png&visual_refresh=true&markers=size:" + config['static_marker_size'] + "%7Ccolor:0x" + config['static_marker_color_gym'] + "%7Clabel:%7C" + str(db_poi_lat) + "," + str(db_poi_lon))
    elif config['static_provider'] == "osm":
        static_map = ("https://www.mapquestapi.com/staticmap/v5/map?locations=" + str(db_poi_lat) + "," + str(db_poi_lon) + "&size=" + str(config['static_width']) + "," + str(config['static_height']) + "&defaultMarker=marker-" + str(config['static_marker_size']) + "-" + config['static_marker_color_gym'] + "&zoom=" + str(config['static_zoom']) + "&key=" + config['static_key'])
    elif config['static_provider'] == "tileserver-gl":
        static_map = (config['static_selfhosted_url'] + "static/klokantech-basic/" + str(db_poi_lat) + "/" + str(db_poi_lon) + "/" + str(config['static_zoom']) + "/" + str(config['static_width']) + "/" + str(config['static_height']) + "/1/png?markers=%5B%7B%22url%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fstop_normal.png%22%2C%22height%22%3A128%2C%22width%22%3A128%2C%22x_offset%22%3A0%2C%22y_offset%22%3A0%2C%22latitude%22%3A%20" + str(db_poi_lat) + "%2C%22longitude%22%3A%20" + str(db_poi_lon) + "%7D%5D")
    elif config['static_provider'] == "mapbox":
        if config['static_fancy']:
            static_map = superfancystaticmap(db_poi_lat, db_poi_lon, config)
            static_map = static_map + ("url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fgym_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])
            static_map = imgur(static_map, config)
        else:
            static_map = ("https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/url-https%3A%2F%2Fraw.githubusercontent.com%2Fccev%2Fstopwatcher%2Fmaster%2Ficons%2Fstaticmap%2Fgym_normal.png(" + str(db_poi_lon) + "," + str(db_poi_lat) + ")/" + str(db_poi_lon) + "," + str(db_poi_lat) + "," + str(config['static_zoom']) + "/" + str(config['static_width']) + "x" + str(config['static_height']) + "?access_token=" + config['static_key'])  
    else:
        static_map = ""  

    if config['imgur_all'] and not config['static_fancy']:
        static_map = imgur(static_map, config)
  
    data = {
        "username": config['gym_unfull_username'],
        "avatar_url": config['gym_img'],
        "embeds": [{
            "title": "Google Maps",
            "url": navigation,
            "color": config['embed_gym_color'],
            "image": {
                "url": static_map
            }
        }]
    }
    result = requests.post(config['webhook_url_gym'], json=data)
    print(result)

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
            check_gyms_query = QUERY_CHECK.format(
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
                lat_small=config['lat_small'],
                lat_big=config['lat_big'],
                lon_small=config['lon_small'],
                lon_big=config['lon_big']
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
    cursor = connect_db(config)

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

print("-------------------------------")
print("First run! Parsing config and checking if your txt files are empty...")
parser = argparse.ArgumentParser()
parser.add_argument(
    "-c", "--config", default="default.ini", help="Config file to use")
args = parser.parse_args()
config_path = args.config
config = create_config(config_path)

cursor = connect_db(config)
db_config(config)
static_config(config)

if not get_portals():
    init.write_portals(cursor, config)
    print("Found an empty portals.txt file - Ran init.py on portals.")
if not get_stops_unfull() or not get_stops_full():
    init.write_stops(cursor, config)
    print("Found an empty stops.txt file - Ran init.py on stops.")
if not get_gyms_unfull() or not get_gyms_full():
    init.write_gyms(cursor, config)
    print("Found an empty gyms.txt file - Ran init.py on gyms.")

main()

while config['dosleep']:
   main()
else:
    print("Looping disabled - Stopping gracefully.")
