# -*- coding: utf-8 -*-

import time
import requests

import mysql.connector as mariadb

webhook_url = ""
api_key = ""


def get_pokestops_full():
    return open("pokestop_full.txt", "r").read().splitlines()

def get_pokestops_unfull():
    return open("pokestop_unfull.txt", "r").read().splitlines()

def get_gyms_unfull():
    return open("gym_unfull.txt", "r").read().splitlines()

def get_gyms_full():
    return open("gym_full.txt", "r").read().splitlines()


def send_webhook_unfull(pokestop_id, lat, lon, api_key):
    navigation_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
    data = {
        "username": "New Pokestop!",
        "avatar_url": "https://raw.githubusercontent.com/ccev/stopwatcher/master/icons/stop.png",
        "embeds": [{
            "title": "Navigation",
            "url": navigation_url,
            "fields": [],
            "image": {
                "url": f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=16&scale=1&size=400x200&maptype=roadmap&key={api_key}&format=png&visual_refresh=true&markers=size:small%7Ccolor:0x13bbec%7Clabel:1%7C{lat},{lon}"
            }
        }]
    }


    result = requests.post(webhook_url, json=data)
    print(f"pokestop unfull webhook: {result}")

    with open("pokestop_unfull.txt", "a") as f:
        f.write(pokestop_id + "\n")

def send_webhook_full(pokestop_id, lat, lon, name, image, api_key):
    navigation_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
    data = {
        "username": "Pokestop Details",
        "avatar_url": "https://raw.githubusercontent.com/ccev/stopwatcher/master/icons/stop.png",
        "embeds": [{
            "title": "Navigation",
            "url": navigation_url,
            "fields": [],
            "image": {
                "url": f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=16&scale=1&size=400x200&maptype=roadmap&key={api_key}&format=png&visual_refresh=true&markers=size:small%7Ccolor:0x13bbec%7Clabel:1%7C{lat},{lon}"
            },
            "thumbnail": {
                "url": image
            },
            "author": {
                "name": name
            }
        }]
    }
    result = requests.post(webhook_url, json=data)
    print(f"pokestop full webhook: {result}")

    with open("pokestop_full.txt", "a") as f:
        f.write(pokestop_id + "\n")

def send_gym_webhook_full(gym, api_key):
    navigation_url = f"https://www.google.com/maps/dir/?api=1&destination={gym['latitude']},{gym['longitude']}"
    data = {
        "username": "New Gym!",
        "avatar_url": "https://raw.githubusercontent.com/ccev/stopwatcher/master/icons/gym.png",
        "embeds": [{
            "title": "Navigation",
            "url": navigation_url,
            "fields": [],
            "image": {
                "url": f"https://maps.googleapis.com/maps/api/staticmap?center={gym['latitude']},{gym['longitude']}&zoom=16&scale=1&size=400x200&maptype=roadmap&key={api_key}&format=png&visual_refresh=true&markers=size:small%7Ccolor:0x13bbec%7Clabel:1%7C{gym['latitude']},{gym['longitude']}"
            },
            "thumbnail": {
                "url": gym["image"]
            },
            "author": {
                "name": gym["name"]
            }
        }]
    }
    result = requests.post(webhook_url, json=data)
    print(f"gym full webhook: {result}")

    with open("gym_full.txt", "a") as f:
        f.write(gym["gym_id"] + "\n")


def check_pokestops(cursor):
    cursor.execute("SELECT pokestop_id, latitude, longitude, name, image FROM pokestop;")

    for pokestop_id, latitude, longitude, name, image in cursor:
        if ((latitude >= FILLIN and latitude <= FILLIN) and (longitude >= FILLIN and longitude <= FILLIN)):
            if image == None:
                if not pokestop_id in get_pokestops_unfull():
                    print("sending unfull", pokestop_id)
                    send_webhook_unfull(pokestop_id, latitude, longitude)
                    time.sleep(1)
            else:
                if not pokestop_id in get_pokestops_full():
                    print("sending full", pokestop_id)
                    send_webhook_full(pokestop_id, latitude, longitude, name, image)
                    time.sleep(1)

def check_gyms(cursor):
    cursor.execute("SELECT gym_id, latitude, longitude FROM gym;")
    gym_data = list(cursor)

    for gym_id, latitude, longitude in gym_data:
        if ((latitude >= FILLIN and latitude <= FILLIN) and (longitude >= FILLIN and longitude <= FILLIN)):
            if not gym_id in get_gyms_full():
                cursor.execute("SELECT name, image FROM pokestop WHERE latitude = %s and longitude = %s", (latitude, longitude))
                gym_extradata = list(cursor)

                if gym_extradata == []:
                    print(f"WARNING: GYM {gym_id}, {latitude} {longitude} didnt have gym extradata??? marking as full!")

                    with open("gym_full.txt", "a") as f:
                        f.write(gym_id + "\n")
                else:
                    gym_dict = {
                        "gym_id": gym_id,
                        "latitude": latitude,
                        "longitude": longitude,
                        "name": gym_extradata[0][0],
                        "image": gym_extradata[0][1]
                    }

                    send_gym_webhook_full(gym_dict)

                    print("updating gym", gym_dict)
                    cursor.execute("UPDATE gymdetails SET name = %s WHERE gym_id = %s", (gym_dict["name"], gym_id))
                    cursor.execute("UPDATE gymdetails SET url = %s WHERE gym_id = %s", (gym_dict["image"], gym_id))
                    cursor.execute("DELETE FROM pokestop WHERE latitude = %s and longitude = %s", (latitude, longitude))
                    print("done")


def main():
    mariadb_connection = mariadb.connect(user='user', password='password', database='dbname')
    cursor = mariadb_connection.cursor()

    check_pokestops(cursor)
    check_gyms(cursor)

    mariadb_connection.commit()


while True:
    main()
    print("loop done! sleeping 500s")
    time.sleep(500)
