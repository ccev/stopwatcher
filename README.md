# Stop Watcher
Stop Watcher is an all-in-one package to stay updated on your local Waypoints. it can:
- Update names/photos of new Gyms and Stops using Portal (or Stop) information
- Delete Stops that converted to Gyms
- Send notifications about new Portals, Stops and Gyms to Discord and Telegram
- Track location, title and photo edits, as well as removals of Portals, Stops and Gyms and send noticiations for them

### Join the [Pogo Tools Discord Server](https://discord.gg/CWFyy6s) for help and updates

Note that a working Ingress Scraper is needed for everything related to Portals and a working MAD/RDM instance for everything related to Stops and Gyms. Stop Watcher will work fine if you only have on of those set up.

## Setup
1. `git clone https://github.com/ccev/stopwatcher.git && cd stopwatcher` and `pip[3[.6]] install -r requirements.txt`
2. `cp -r config_example config`, fill out config/config.ini, config/filters.json and config/geofence.json. The geofence file uses the same format as Poracle, so you can copy from there or just follow the example. Config and filters are explained below.
3. That's it. Now run `python3 stop_watcher.py`. I recommend using cron or pm2 to loop it

## Additional Steps
### Static Maps
Mapbox and tileserver static maps are the coolest ones. If you don't already have one of the four providers set up, I'd recommend making a free [Mapbox](https://www.mapbox.com/) account for 50,000 free requests.

#### [Flo's Tileserver](https://github.com/123FLO321/SwiftTileserverCache)
To get working tileserver Static Maps, make sure you're on the latest version (>1.0.3 / March 4 2020), then copy stopwatcher.json to the `Templates` folder in your TileServer directory

### Ingress Scraper
Use [ClarkyKent's ingress scraper](https://github.com/ClarkyKent/ingress_scraper) for everything related to Portals. Have it loop and put the restart delay in Stop Watcher's config

## Notification Examples
#### Mapbox
![](https://i.imgur.com/AvBkt8O.png)
#### Google
![](https://i.imgur.com/ETd8Jig.png)
#### OSM (Mapquest)
![](https://i.imgur.com/X0M1Esh.png)

## filters.json
Filters tell Stop Watcher what to look for and where to send it. Every filter option is optional, except `"area"`. So if you don't want something, just delete the option to avoid confusion (e.g. remove `"webhook"` completely instead of putting `"webhook": []` if you don't want Discord notifications)

| Option | Description | What to put in
|-|-|-|
| **`"area"`** | Needs to match an area name from your geofence.json, else it will default to your whole DB. | String, `"berlin"`
| **`"update"`** | What kind of Waypoints' photos/titles you want to get updates, if they're empty. Works with Stops and Gyms. Stops take their info from Portal, Gyms from Stops or Portals. | List with "stop" and/or "gym" in, `["stop", "gym"]` |
| **`"delete_converted_stops"`** | Whether to delete Stops that turned into Gyms or not. You can just delete the option instead of putting in `false` | `true`/`false` |
| **`"send"`** | The kinds of new Waypoints you want to get sent. | List with "portal", "stop" and/or "gym", `["portal", "stop", "gym"]` |
| **`"send_empty"`** | Whether or not to send Stops/Gyms with no photo/title. If true, the Waypoint will be sent again if its info is known. If you have an Ingress Scraper running and updates set to true, you can leave this option on, in case the systems fail. You can just delete the option instead of putting in `false` | `true`/`false`
| **`"edits"`** | The kinds of Waypoints you want edits to be sent of. | List with "portal", "stop" and/or "gym", `["portal", "stop", "gym"]` |
| **`edit_types`** | The kinds of edits you want to get sent. (Should have at least one if `"edits"` has something in) | List with "location", "title" and/or "photo", `["location", "title", "photo"]` |
| **`webhook`** | The Discord Webhook edited/new waypoints should get sent to. Can also be multiple | Webhook links, `["url.com"]` or `["url.com","url2.com"]` |
| **`bot_id`** | You Telegram's Bot ID | String, `"8762682"` |
| **`chat_id`** | You Telegram's Chat ID. Can also be multiple. (Needs a set `"bot_id"` to work) | Chat IDs, `["24254535"]` or `["4636363","970785"]` |
