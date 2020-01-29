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

    return mydb

def db_config(config):
    if config['db_scan_schema'] == "mad":
        config['db_stop_table'] = "pokestop"
        config['db_stop_id'] = "pokestop_id"

        config['db_gym_table'] = "gym"
        config['db_gym_id'] = "gym_id"

    if config['db_scan_schema'] == "rdm":
        config['db_stop_table'] = "pokestop"
        config['db_stop_id'] = "id"

        config['db_gym_table'] = "gym"
        config['db_gym_id'] = "id"

    if config['db_portal_schema'] == "pmsf":
        config['db_portal_table'] = "ingress_portals"
        config['db_portal_id'] = "external_id"

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
        check_portals_query = QUERY_CHECK.format(
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
        check_stops_query = QUERY_CHECK.format(
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
        check_gyms_query = QUERY_CHECK.format(
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="default.ini", help="Config file to use")
    args = parser.parse_args()
    config_path = args.config
    config = create_config(config_path)

    mydb = connect_db(config)
    cursor = mydb.cursor()
    db_config(config)

    write_portals(cursor, config)
    write_stops(cursor, config)
    write_gyms(cursor, config)

    cursor.close()
    mydb.close()
    print("Done.")