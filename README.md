![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)

# Stop Watcher
Discord Webhooks for new Stops, Gyms and Portals. Will also help with updating names/images and deleting Stops that turned into Gyms.

## Notes
- This project is pretty new, so there's a high chance for errors. If you have any questions, feel free to DM me on Discord (Malte#3333)
- Only tested for python3.6 - no idea if anything is working on other python versions
- The Script will work perfectly fine if you don't track Portals. I do still recommend to have an extra Portal Scraper Script running.
- `stop_watcher.py`, `edit_watcher.py` and `init.py` can be run with `-c whatever.ini` to use a custom config file. Should help if you want to use the script for multiple areas or discord channels

## Usage
1. `git clone https://github.com/ccev/stopwatcher.git && cd stopwatcher`, `pip[3[.6]] install -r requirements.txt`, then copy and rename `default.ini.example` to `default.ini` and configure everything. Refer to the table below if you're not sure about specific variables. 
2. IMPORTANT: Before you even touch `stop_watcher.py`, run `init.py` once! This will fill in the cache files with all stops/gyms/portals in your database.
3. After configuring `default.ini` and running `init.py` you can start the main script using `python[3[.6]] stop_watcher.py`
4. Set up [ClarkyKent's ingress scraper](https://github.com/ClarkyKent/ingress_scraper) and have it running every few hours to get working webhooks for new portals

## Edit Watcher
There's an additional script in this repo, the `edit_watcher.py`. This will track any changes made to Portal titles, locations and images in your given area and send them to the given Webhook. Note that this only works for Portals.

To enable it, go to the `[Edit Watcher]` part of your config file and fill in `EXTRA_PORTAL_DB_NAME`, `EXTRA_PORTAL_TABLE` and `WEBHOOK_URL`. The first two options are the names for an additional table needed. I recommend to put your manualdb name for `EXTRA_PORTAL_DB_NAME` and `editwatcher_portals` for `EXTRA_PORTAL_TABLE`. The Script will create the table for you. For additional info, please refer to the table below.

## Static Maps
### Examples
#### Mapbox (Super Fancy mode)
![Super Fancy](https://i.imgur.com/AvBkt8O.png)
#### Mapbox
![Mapbox](https://i.imgur.com/woB2WiR.png)
#### Google
![Google](https://i.imgur.com/ETd8Jig.png)
#### OSM (Mapquest)
![Mapquest](https://i.imgur.com/X0M1Esh.png)
### Usage
1. Super Fancy mode:
- I'd recommend to have Super Fancy mode enabled. It will show all surrounding Stops/Gyms in the static map. To use it, you'll need to have `SUPER_FANCY_STATIC_MAPS` enabled, have a working Imgur Client ID and use mapbox as your `PROVIDER`.
2. Imgur:
- Since Super Fancy Static Map URLs are likely to exceed Discord's 2000 character limit, you'll need an Imgur Client ID. I also recommend to turn on `USE_IMGUR_MIRRORS_FOR_EVERYTHING` which will also mirror other types of static maps to Imgur. This will help to protect your API keys and prevents possibly reaching the 2000 character limit.
- To get your Imgur Client ID, go to https://api.imgur.com/oauth2/addclient, sign in, tick `OAuth 2 authorization without a callback URL` and then fill out `Application name:`, `Email:` and `Description:`. It does not matter what you put in. Solve the captcha and click `submit`. Now copy the Client ID.
3. Providers:
- Mapbox: Go to https://www.mapbox.com/, click `Start mapping for free`, log in and copy the Key. Limit: 50,000
- Google: I recommend following https://pa.readthedocs.io/en/master/miscellaneous/location-services.html to enable Google Static Maps
- Mapquest: Go to https://developer.mapquest.com/, click `Get your Free API Key`, log in and copy the Key. Limit: 15,000/month
- tileserver-gl: https://github.com/123FLO321/SwiftTileserverCache
4. Marker Size:
- This, as well as the color options, are only needed for Google and OSM static Maps
- For Google Static Map you can put numbers from 0 to 3
- For OSM Static Map you can put numbers from 1 to 3

## Config
| Variable | Description | What to put in |
|-|-|-|
| `STOPS` | Enable/Disable checks for stops | True/False |
| `GYMS` | Enable/Disable checks for gyms | True/False |
| `PORTALS` | Enable/Disable checks for portals | True/False |
| `GYM_UPDATE_THROUGH_STOP` | Check for gyms without name/image, then copy them from the corresponding stop | True/False |
| `GYM_UPDATE_THROUGH_PORTAL` | Check for gyms without name/image, then copy them from the corresponding portal | True/False |
| `STOP_UPDATE_THROUGH_PORTAL` | Check for stops without name/image, then copy them from the corresponding portal | True/False |
| `DELETE_CONVERTED_STOP` | Delete stops that turned into gyms after updating the gym info. Needs to have `GYM_UPDATE_THROUGH_STOP` or `GYM_UPDATE_THROUGH_PORTAL` enabled | True/False |
| `MIN_LAT` `MAX_LAT` `MIN_LON` `MAX_LON` | Defines the area the script will be touching things in | Coordinates |
| `LOOP` | If enabled, the script will loop itself. If disabled, it will stop after running once | True/False |
| `SECONDS_BETWEEN_LOOPS` | How many seconds to wait between loops | Amount of seconds |

### Embeds
| Variable | Description | What to put in |
|-|-|-|
| `STOP_IMAGE` | Avatar image for stop webhooks | Link |
| `STOP_DETAILS_USERNAME` | Username for stop webhooks with known name/image | Text |
| `STOP_NO_DETAILS_USERNAME` | Username for stop webhooks with unknown name/image | Text |
| `STOP_COLOR` | Color for stop webhooks | Decimal value |
| `GYM_IMAGE` | Avatar image for gym webhooks | Link |
| `GYM_DETAILS_USERNAME` | Username for gym webhooks with known name/image | Text |
| `GYM_NO_DETAILS_USERNAME` | Username for gym webhooks with unknown name/image | Text |
| `GYM_COLOR` | Color for gym webhooks | Decimal value |
| `PORTAL_IMAGE` | Avatar image for portal webhooks | Link |
| `PORTAL_USERNAME` | Username for portal webhooks | Text |
| `PORTAL_COLOR` | Color for portal webhooks | Decimal value |

### Static Map
| Variable | Description | What to put in |
|-|-|-|
| `PROVIDER` | What type of Static Map you want. If put `none` Static Maps will be disabled. | mapbox/tileserver-gl/google/osm/none |
| `SUPER_FANCY_STATIC_MAPS` | Enable/Disable Super Fancy Static Maps | True/False |
| `KEY` | Your API key for the Static Map service you configured | API Key |
| `ZOOM` | Zoom for Static Maps | Number |
| `WIDTH` `HEIGHT` | Width and height for Static Maps | Number |
| `USE_IMGUR_MIRRORS_FOR_EVERYTHING` | Enable/Disable Imgur mirroring to all types of Static Maps | True/False |
| `IMGUR_CLIENT_ID` | Your Imgur Client ID | Imgur Client ID |
| `MARKER_COLOR_STOP` | Pokestop marker color for Google and OSM Static Maps | Hex color |
| `MARKER_COLOR_GYM` | Gym marker color for Google and OSM Static Maps | Hex color |
| `MARKER_COLOR_PORTAL` | Portal marker color for Google and OSM Static Maps | Hex color |
| `MARKER_SIZE` | Marker size for Google and OSM Static Maps | 0-3 |
| `TILESERVER_URL` | The URL of your self hosted tileserver (only needed for `tileserver-gl`) | URL |

### Edit Watcher
| Variable | Description | What to put in |
|-|-|-|
| `ENABLE` | Enable/Disable tracking of Portal edits | True/False |
| `EXTRA_PORTAL_DB_NAME` | Name of the DB in which your extra Portal table should be in | Text |
| `EXTRA_PORTAL_TABLE` | The name of your extra Portal table | Text |
| `WEBHOOK_URL` | The Webhook URL all tracked Edits will be sent to | URL |
| `USERNAME` | Username used for Portal Edit Discord Webhooks | Text |
| `IMAGE` | Image used for Portal Edit Discord Webhooks | Link |
| `LOCATION_EDIT_TITLE` `TITLE_EDIT_TITLE` `IMAGE_EDIT_TITLE` | Can be used to translate your messages. The embed title will always look like this: "`[Portal Name] [Title Config Option]`" | Text |
| `FROM` `TO` | Can be used to translate your messages. The embed text will always look like this: "`From [Previous info] \n To [New Info]`" | Text |

### DB
| Variable | Description | What to put in |
|-|-|-|
| `SCANNER_DB` | The type of scanner you're using | mad/rdm/none |
| `PORTAL_DB` | The type of db you're using for portals | pmsf/none |
| `HOST` `PORT` `USER` `PASSWORD` | Credentials used to connect to your MySQL databases | Credentials |
| `NAME` | Name of your Scanner DB | Text |
| `PORTAL_DB_NAME` | Name of your Portal DB | Text |
| - | If you're not using a supported DB schema, you can put "none" for `SCANNER_DB` or `PORTAL_DB` and fill out the last section of the config with your info | - |

## Credits
- [kittenswolf](https://github.com/kittenswolf) for making this script's base
- [PMSFnestScript](https://github.com/M4d40/PMSFnestScript) for having its code teach me 70% of my python knowledge.
