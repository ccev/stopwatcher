import json
import time
import requests
import pyshorteners

from urllib.parse import quote, quote_plus

from util.s2cells import s2cell

def create_static_map(config, queries, type_, lat, lon, marker_color):
    with open("config/templates.json", encoding="utf-8") as f:
        templates = json.load(f)

    new_template = None
    for t in templates["static_map"]:
        if type_ in t["for"]:
            new_template = t
            break

    template = {
        "provider": config.static_provider,
        "key": config.static_key,
        "style": "",
        "scale": 1,
        "zoom": 17,
        "width": 800,
        "height": 500,
        "17-s2cell": False,
        "s2cell-fill": "",
        "s2cell-stroke": "",
        "s2cell-stroke-width": 2,
        "markers": "",
        "marker-color": marker_color
    }
    if type_ == "portal":
        template["17-s2cell"] = True

    if "provider" in new_template:
        template["provider"] = new_template["provider"]

    if template["provider"] == "tileserver":
        template["style"] = "osm-light"
        template["zoom"] = 17.5
        template["markers"] = "https://raw.githubusercontent.com/ccev/stopwatcher-icons/master/tileserver/"
        template["cell_fill"] = "#ffffff60"
        template["cell_stroke"] = "#c7c7c7"
        template["cell_width"] = 2

    elif template["provider"] == "mapbox":
        template["style"] = "dark-v10"
        template["zoom"] = 16
        template["markers"] = "https://raw.githubusercontent.com/ccev/stopwatcher-icons/master/mapbox/"
        template["cell_fill"] = "#ffffff60"
        template["cell_stroke"] = "#c7c7c7"
        template["cell_width"] = 2

    elif template["provider"] == "google":
        template["style"] = "roadmap"

    for key in template.keys():
        if key in new_template:
            template[key] = new_template[key]

    if template["provider"] == "google" or template["provider"] == "osm":
        template["17-s2cell"] = False

    # STATIC MAP GENERATION
    pathjson = ""
    geojson = ""
    if template["17-s2cell"]:
        cell = s2cell(queries, lat, lon, 17)
        pathjson = f"&pathjson={quote(str(cell.tileserver()))}"
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "stroke": template['s2cell-stroke'],
                        "stroke-width": template['s2cell-stroke-width'],
                        "stroke-opacity": 1,
                        "fill": template['s2cell-fill'],
                        "fill-opacity": 0.5
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            cell.mapbox()
                        ]
                    }
                }
            ]
        }
        geojson = f"geojson({quote(json.dumps(geojson))}),"


    static_map = ""         
    if config.static_provider == "google":
        static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={template['zoom']}&scale={template['scale']}&size={template['width']}x{template['height']}&maptype={template['style']}&key={template['key']}&format=png&visual_refresh=true&markers=size:normal%7Ccolor:0x{template['marker-color']}%7Clabel:%7C{lat},{lon}"
    elif config.static_provider == "mapquest":
        static_map = f"https://www.mapquestapi.com/staticmap/v5/map?locations={lat},{lon}&size={template['width']},{template['height']}&defaultMarker=marker-md-{template['marker-color']}&zoom={template['zoom']}&key={template['key']}"
    elif config.static_provider == "tileserver":
        limit = 30
        static_list = json.loads("[]")
        if type_ == "portal":
            portals = queries.static_portals(limit, lat, lon)
            for lat_, lon_, dis in portals:
                static_list.append([lat_,lon_,"portal"])
        else:
            waypoints = queries.static_waypoints(limit, lat, lon)
            for lat_, lon_, w_type, dis in waypoints:
                static_list.append([lat_,lon_,w_type])

        static_map = f"{template['key']}staticmap/stopwatcher_beta?style={template['style']}&lat={lat}&lon={lon}&zoom={template['zoom']}&width={template['width']}&height={template['height']}&scale={template['scale']}&fill={quote(template['s2cell-fill'])}&stroke={quote(template['s2cell-stroke'])}&stroke-width={template['s2cell-stroke-width']}&type={type_}{pathjson}&pointjson={quote(json.dumps(static_list))}&markers={quote_plus(template['markers'])}"
        requests.get(static_map)
    elif config.static_provider == "mapbox":
        limit = 32
        static_map = f"https://api.mapbox.com/styles/v1/mapbox/{template['style']}/static/{geojson}"
        if type_ == "portal":
            portals = queries.static_portals(limit, lat, lon)
            for lat_, lon_, dis in portals:
                static_map = static_map + f"url-{quote_plus(template['markers'])}portal_gray.png({lon_},{lat_}),"
        else:
            waypoints = queries.static_waypoints(limit, lat, lon)
            for lat_, lon_, w_type, dis in waypoints:
                static_map = static_map + f"url-{quote_plus(template['markers'])}{w_type}_gray.png({lon_},{lat_}),"
        static_map = static_map + f"url-{quote_plus(template['markers'])}{type_}_normal.png({lon},{lat})/{lon},{lat},{template['zoom']}/{template['width']}x{template['height']}?access_token={template['key']}"
    
    # HOSTING
    print(static_map)

    if config.host_provider == "tinyurl":
        short = pyshorteners.Shortener().tinyurl.short
        try:
            static_map = short(static_map)
        except:
            static_map = ""

    elif config.host_provider == "imgur":
        imgur_success = False
        while not imgur_success:
            payload = {'image': static_map}
            headers = {'Authorization': f'Client-ID {config.host_key}'}
            result = requests.post(url="https://api.imgur.com/3/image/", data=payload, headers=headers)
            data = result.json()["data"]
            if "error" in data:
                if data["error"]["code"] == 429:
                    print("Hit Imgur's rate limit. Sleeping 1 hour.")
                    time.sleep(3600)
                else:
                    print("Imgur error :S please report - trying again in 1 minute")
                    print(static_map)
                    print(data)
                    time.sleep(60)
            elif "id" in data:
                image_id = data["id"]
                static_map = f"https://i.imgur.com/{image_id}.png"
                imgur_success = True
            else:
                print("Some weird Imgur stuff. Please report this log entry!! - trying again in 1 minute")
                print(static_map)
                print(data)
                time.sleep(60)

    elif config.host_provider == "polr":
        key = list(config.host_key.split(","))
        polr_payload = {"key": key[1], "url": static_map, "is_secret": "false"}
        result = requests.get(f"{key[0]}/api/v2/action/shorten?key={key[1]}", params=polr_payload)
        static_map = result.text

    return static_map