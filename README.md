![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)

# Stop Watcher
Discord Webhooks for new Stops, Gyms and Portals. Will also help with updating names/images and deleting Stops that turned into Gyms.

## Notes
- Get support on the [PMSF Discord Server](https://discord.gg/AkBq4yn)
- Tested for python3.6 - should be working on newer versions, shouldn't work with older python2
- The Script will work perfectly fine if you don't track Portals. I do still recommend to have an extra Portal Scraper Script running.
- `stop_watcher.py` and `edit_watcher.py` can be run with `-c whatever.ini` to use a custom config file. Should help if you want to use the script for multiple areas or discord channels

## Usage
1. `git clone https://github.com/ccev/stopwatcher.git && cd stopwatcher`, `pip[3[.6]] install -r requirements.txt`, then copy and rename `default.ini.example` to `default.ini` and configure everything. Refer to the table below if you're not sure about specific variables. 
2. Start stopwatcher using `python[3[.6]] stop_watcher.py`
3. Set up [ClarkyKent's ingress scraper](https://github.com/ClarkyKent/ingress_scraper) and have it running every few hours to get working webhooks for new portals

## Edit Watcher
There's an additional script in this repo, the `edit_watcher.py`. This will track any changes made to Portal titles, locations and images in your given area and send them to the given Webhook. Note that this only works for Portals.

To enable it, fill in the `[Edit Watcher]` part of your config. The Script will create the extra table for you in the given Database. For additional info, please refer to the table below.

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
- I'd recommend to have Super Fancy mode enabled. It will show all surrounding Stops/Gyms in the static map. To use it, you'll need to have `SUPER_FANCY_STATIC_MAPS` enabled, a working Imgur Client ID and use mapbox as your `PROVIDER`.
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
| `BBOX` | Defines the area the script will be touching things in. Go to [bboxfinder.com](http://bboxfinder.com/), draw a rectangle copy the coordinates next to `Box` in the bottom window. | bbox |
| `CHAT_APP` | Define which chat app to send Webhooks to | discord/telegram |
| `LANGUAGE` | What language should the messages be in? (custom languages can be created by copying locale/en.json and renaming it to whatever you put in here) | en/de/pl |
| `LOOP` | If enabled, the script will loop itself. If disabled, it will stop after running once | True/False |
| `SECONDS_BETWEEN_LOOPS` | How many seconds to wait between loops | Amount of seconds |

### Discord
| Variable | Description | What to put in |
|-|-|-|
| `STOP_IMAGE` | Avatar image for stop webhooks | Link |
| `STOP_COLOR` | Color for stop webhooks | Decimal value |
| `GYM_IMAGE` | Avatar image for gym webhooks | Link |
| `GYM_COLOR` | Color for gym webhooks | Decimal value |
| `PORTAL_IMAGE` | Avatar image for portal webhooks | Link |
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
| `IMAGE` | Image used for Portal Edit Discord Webhooks | Link |
| `DELETED_TIMESPAN` | Edit Watcher will only consider Portals as deleted if they haven't been updated in (this many) seconds | time in s |
| `DELETED_LIMIT` | If more than (this) many Portals haven't been updated in a while, they won't be marked as deleted. (To prevent false messages if your Scraper cookie ran out) | Number |

### DB
| Variable | Description | What to put in |
|-|-|-|
| `SCANNER_DB_SCHEMA` | The type of scanner you're using | mad/rdm/none |
| `PORTAL_DB_SCHEMA` | The type of db you're using for portals | pmsf/none |
| `HOST` `PORT` `USER` `PASSWORD` | Credentials used to connect to your MySQL databases | Credentials |
| `SCANNER_DB_NAME` | Name of your Scanner DB | Text |
| `PORTAL_DB_NAME` | Name of your Portal DB | Text |

## Credits
- [kittenswolf](https://github.com/kittenswolf) for making this script's base
- [PMSFnestScript](https://github.com/M4d40/PMSFnestScript) for having its code teach me 70% of my python knowledge.
