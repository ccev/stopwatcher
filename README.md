# stopwatcher
An easy way to send webhooks for new stops and gyms in your scan area.

Still very WIP.
- Config.ini won't do anything. It just holds some ideas for a possible config
- hardcoded for MAD with Discord Webhooks
- fill out db stuff at the buttom, coordinates (search for "FILLIN") and put in the google api key and webhook url at the top
- be advised that the script will think that all stops + gyms in your db are new on the very first run
- be advised that it's currently going to delete all stops that turned into a gym. Maybe check if that's not breaking anything before running.
