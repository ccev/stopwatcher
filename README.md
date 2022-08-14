# Stop Watcher

Stop Watcher is a tool for tracking changes to Niantic's Real World POI platform. 
These POIs are referred to as Forts in this project.


## Data Input

Stop Watcher accepts multiple data sources, mainly an Intel Scraper or a 
Pokémon GO Scanner like RDM. Specifically it supports

- Custom Webhooks for direct integration with other projects
- Raw Pogo Protos
- RDM, MAD and Intel Watcher databases


## Data Output

- Stop Watcher keeps its own database of any Forts it receives, 
that's always kept updated
- Discord notifications for changes
- WIP: Telegram notifications
- WIP: Ougoing Webhooks for direct integration with other projects like Poralce


## Setup

- Clone the repo, `cp -r config.example config` and 
`pip install -r requirements.txt`
- Run the file(s) in `sql/` on any MySQL database you like
- Fill out `config/config.toml`
- Run the project using `python stop_watcher.py`. Due to dependancy limitations, 
Python 3.8-3.10 is required. 3.11 may work on Linux

### Geofence format

If you want to receive notifications, you likely only want them for certain areas, 
so Stop Watcher requires geofences to filter unwanted Forts out. In the config, 
you can define any path that contains Geofence files, by default it's in 
`config/geofences`.

In this directoy, there should be at least one geofence file for every configured 
area and with a `.txt` extension. The name of the file has to match the name of 
the configured are. That name can also be overwritten within the file. The file 
has to look as follows.

```
[geofence name]  # this is optional and only overwrites the file name
lat,lon
lat,lon
...
```

## More

### How Stop Watcher detects removals

TBD

### Custom Webhooks as input

Webhooks are accepted as a POST request to the configured endpoint and require 
an HTTP basic auth username and password.

#### Format

```json
[
    {
        "id": "string",
        "type": "pokestop/gym/portal/lightship_poi",
        "lat": 0.0,
        "lon": 0.0,
        "name": "optional: string",
        "description": "optional: string",
        "cover_image": "optional: string"
    },
    {
        "id": "8bda87242a1c491f8964324a374f9335.12",
        "type": "gym",
        "lat": 52.516240,
        "lon": 13.377708,
        "name": "Brandenburger Tor",
        "cover_image": "http://lh3.googleusercontent.com/8F-55jfIGCeLp-CeLJ5Qa6itm7CgzpeuWrgX9igaU6Gq2TWpEHN_duhAoiEoBb3veT2Cib1fU6HIHehLPStRyW-kw64"
    }
]
```