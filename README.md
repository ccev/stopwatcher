# Stop Watcher
An easy way to send webhooks for new stops and gyms in your scan area.

## Notes
- This project is brand new, so very little testing has been done.
- BACKUP YOUR DATABASE - I cannot guarantee the script correctly working for your setup.
- python3.6 only
- Made for MAD and PMSF databases but should be compatible with RDM and other services with the right config. Better compatibility is planned
- DO NOT FORGET TO RUN `init.py` ONCE!
- Please have a Ingress Scraper running if you enable anything related to portals

## Usage
1. `pip[3[.6]] install -r requirements.py`, then copy and rename `default.ini.example` to `default.ini` and fill it in 
2. IMPORTANT: Before you even touch `stop_watcher.py`, be sure to run `init.py` once! This will fill in the cache files. If you're adding big amounts of Stops/Gyms/Portals to your area or change the area in config or expanding the area, I'd recommend to run `init.py` again.
3. After filling out `default.ini` and running `init.py` you can start the script using `python[3[.6]] stop_watcher.py`
4. Set up [ClarkyKent's ingress scraper](https://github.com/ClarkyKent/ingress_scraper) and have it running every few hours to get working webhooks for new portals

## Config

### Config
| Variable | Description | What to put in |
|-|-|-|
| `STOPS` | Enable/Disable checks & sending of stops | True/False |
| `GYMS` | Enable/Disable checks & sending of gyms | True/False |
| `PORTALS` | Enable/Disable checks & sending of portals | True/False |
| `GYM_UPDATE_THROUGH_STOP` | Check for gyms without name/image, then copy them from the corresponding stop | True/False |
| `GYM_UPDATE_THROUGH_PORTAL` | Check for gyms without name/image, then copy them from the corresponding portal | True/False |
| `STOP_UPDATE_THROUGH_PORTAL` | Check for stops without name/image, then copy them from the corresponding portal | True/False |
| `DELETE_CONVERTED_STOP` | Delete stops that turned to gyms, after updating them. Needs to have `GYM_UPDATE_THROUGH_STOP` or `GYM_UPDATE_THROUGH_STOP` enabled | True/False |
| `MIN_LAT` `MAX_LAT` `MIN_LON` `MAX_LON` | Area in which the script's running | Coordinates |
| `LOOP` | If enabled, the script will loop itself. If disabled, it will stop after running once | True/False |
| `SECONDS_BETWEEN_LOOPS` | How many seconds to wait in between loops | Amount of seconds |

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

## Credits
- [kittenswolf](https://github.com/kittenswolf) for making this script's base
- [PMSFnestScript](https://github.com/M4d40/PMSFnestScript) for having its code teach me 70% of my python knowledge.
