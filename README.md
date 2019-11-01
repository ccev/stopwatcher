# Stop Watcher
An easy way to send webhooks for new stops and gyms in your scan area.

## Notes
- This project is brand new, so very little testing has been done.
- BACKUP YOUR DATABASE just in case - again; very little testing has been done.
- python3.6 only
- **DO NOT FORGET TO RUN `init.py` BEFORE RUNNING `stop_watcher.py` FOR THE FIRST TIME**!
- I recommend having an automated Ingress Scraper running if you enable anything related to portals

## Usage
1. `git clone https://github.com/ccev/stopwatcher.git && cd stopwatcher`, `pip[3[.6]] install -r requirements.py`, then copy and rename `default.ini.example` to `default.ini` and configure everything. Refer to the table below if you're not sure about specific variables. 
2. IMPORTANT: Before you even touch `stop_watcher.py`, run `init.py` once! This will fill in the cache files with all stops/gyms/portals in your database.
3. After configuring `default.ini` and running `init.py` you can start the main script using `python[3[.6]] stop_watcher.py`
4. Set up [ClarkyKent's ingress scraper](https://github.com/ClarkyKent/ingress_scraper) and have it running every few hours to get working webhooks for new portals

## Config
| Variable | Description | What to put in |
|-|-|-|
| `STOPS` | Enable/Disable checks for stops | True/False |
| `GYMS` | Enable/Disable checks for gyms | True/False |
| `PORTALS` | Enable/Disable checks for portals | True/False |
| `GYM_UPDATE_THROUGH_STOP` | Check for gyms without name/image, then copy them from the corresponding stop | True/False |
| `GYM_UPDATE_THROUGH_PORTAL` | Check for gyms without name/image, then copy them from the corresponding portal | True/False |
| `STOP_UPDATE_THROUGH_PORTAL` | Check for stops without name/image, then copy them from the corresponding portal | True/False |
| `DELETE_CONVERTED_STOP` | Delete stops that turned into gyms after updating the gym info. Needs to have `GYM_UPDATE_THROUGH_STOP` or `GYM_UPDATE_THROUGH_STOP` enabled | True/False |
| `MIN_LAT` `MAX_LAT` `MIN_LON` `MAX_LON` | Defines the area the script will be touching things in | Coordinates |
| `LOOP` | If enabled, the script will loop itself. If disabled, it will stop after running once | True/False |
| `SECONDS_BETWEEN_LOOPS` | How many seconds to wait between loops | Amount of seconds |

### Embeds
| Variable | Description | What to put in |
|-|-|-|
| `STOP_IMAGE` | Avatar image for stop webhooks | Link |
| `STOP_DETAILS_USERNAME` | Username for stop webhooks with known name/image | Text |
| `STOP_NO_DETAILS_USERNAME` | Username for stop webhooks with unknown name/image | Text |
| `GYM_IMAGE` | Avatar image for gym webhooks | Link |
| `GYM_DETAILS_USERNAME` | Username for gym webhooks with known name/image | Text |
| `GYM_NO_DETAILS_USERNAME` | Username for gym webhooks with unknown name/image | Text |
| `PORTAL_IMAGE` | Avatar image for portal webhooks | Link |
| `PORTAL_USERNAME` | Username for portal webhooks | Text |

### Static Map
| Variable | Description | What to put in |
|-|-|-|
| `ENABLE` | Enable/Disable static maps | True/False |
| `G_API_KEY` | Your Google API key | API Key |
| `G_ZOOM` | Zoom for Google Static Maps | Number |
| `G_RESOLUTION` | Width and height for Google Static Maps | WIDTHxHEIGHT |
| `G_MARKER_COLOR_STOP` | Pokestop marker color for Google Static Maps | Hex color |
| `G_MARKER_COLOR_GYM` | Gym marker color for Google Static Maps | Hex color |
| `G_MARKER_COLOR_PORTAL` | Portal marker color for Google Static Maps | Hex color |
| `G_MARKER_SIZE` | Marker size for Google Static Maps | tiny/small/mid |

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
