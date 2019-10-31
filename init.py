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

QUERY_CHECK = """SELECT {db_id} FROM {db_dbname}.{db_table}"""
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
    config['db_gym_table'] = config_raw.get(
        'DB',
        'GYM_TABLE')
    config['db_gym_id'] = config_raw.get(
        'DB',
        'GYM_ID')
    config['db_portal_table'] = config_raw.get(
        'DB',
        'PORTAL_TABLE')
    config['db_portal_id'] = config_raw.get(
        'DB',
        'PORTAL_ID')
    return config

def connect_db(config):
    print("Initializing")
    mydb = connect(
        host=config['db_host'],
        user=config['db_user'],
        passwd=config['db_pass'],
        database=config['db_dbname'],
        port=config['db_port'],
        autocommit=True)

    cursor = mydb.cursor()

    return cursor

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
        check_portals_query = QUERY_CHECK.format(
            db_id=config['db_portal_id'],
            db_dbname=config['db_portal_dbname'],
            db_table=config['db_portal_table']
        )
        cursor.execute(check_portals_query)
        portals = cursor.fetchall()

        for db_portal_id in portals:
            if not portals[0][0] in get_portals():
                print("Writing portal id", portals[0][0])
                with open("txt/portals.txt", "a") as f:
                    f.write(portals[0][0] + "\n")

def write_stops(cursor, config):
    if config['send_stops']:
        check_stops_query = QUERY_CHECK.format(
            db_id=config['db_stop_id'],
            db_dbname=config['db_dbname'],
            db_table=config['db_stop_table']
        )
        cursor.execute(check_stops_query)
        stops = cursor.fetchall()

        for db_stop_id in stops:
            if not stops[0][0] in get_stops_full():
                print("Writing full stop id", stops[0][0])
                with open("txt/stop_full.txt", "a") as f:
                    f.write(stops[0][0] + "\n")
            if not stops[0][0] in get_stops_unfull():
                print("Writing unfull stop id", stops[0][0])
                with open("txt/stop_unfull.txt", "a") as f:
                    f.write(stops[0][0] + "\n")

def write_gyms(cursor, config):
    if config['send_gyms']:
        check_gyms_query = QUERY_CHECK.format(
            db_id=config['db_gym_id'],
            db_dbname=config['db_dbname'],
            db_table=config['db_gym_table']
        )
        cursor.execute(check_gyms_query)
        gyms = cursor.fetchall()

        for db_gym_id in gyms:
            if not gyms[0][0] in get_gyms_full():
                print("Writing full gym id", gyms[0][0])
                with open("txt/gym_full.txt", "a") as f:
                    f.write(gyms[0][0] + "\n")
            if not gyms[0][0] in get_gyms_unfull():
                print("Writing unfull gym id", gyms[0][0])
                with open("txt/gym_unfull.txt", "a") as f:
                    f.write(gyms[0][0] + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="default.ini", help="Config file to use")
    args = parser.parse_args()
    config_path = args.config
    config = create_config(config_path)

    cursor = connect_db(config)

    write_portals(cursor, config)
    write_stops(cursor, config)
    write_gyms(cursor, config)

    cursor.close()
    print("Done.")