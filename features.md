# Features
A detailed overview of what Stop Watcher can do.

## Notifications for new Stops, Gyms and Portals
![](https://i.imgur.com/Q3n44sC.png)

Set up Stop Watcher to receive notifications for new Waypoints in your area. All notifications are able to show a Static Map (which is also showing additional Waypoints naerby), the Waypoint's address and a custom Map link.

## Detailed information about new Portals
![](https://i.imgur.com/BCAsy9g.png)

Portal notifications tell you if it's converting to a Pokestop (or Gym), if it's triggering a gym, the amount of Stops/Gyms in its L14 cell and when it'll convert. Notifications for Portal Location edits have similiar information.

## Edit/Removal tracking
![](https://i.imgur.com/lBRrPPP.png)

Stop Watcher can track Title, Location and Photo Edits, as well as Removals of Stops, Gyms and Portals.

## Keeping your database updated
- Upon creation, Stop Watcher can update a Stop's or Gym's photo/title with Stop/Portal information
- It can delete Stops that converted into Gyms
- When a Portal's title is changed, it can update the title of the corresponding Gym (your scanner will never pick up that information)
- A tool to compare Stops/Gyms to their corresponding Portals and update them accordingly (if your Intel Watcher area is bigger than your scanner area)
- A tool to sum up picked up removals, so you can review and delete them from your DB.

## Customization
Stop Watcher is designed to work without setting much up but can be highly configured.
- [Filters](https://github.com/ccev/stopwatcher#filtersjson): Tell Stop Watcher what to do for multiple areas
- [Templates](https://github.com/ccev/stopwatcher#templatesjson): Customize Static Maps and Geocoding

## Support
- Works without a Portal Scraper or without a scanner
- Languages: Englisch, German, French, Spanish and Polish
- Scanners: MAD and RDM
- Chat Apps: Discord and Telegram
- Static Maps: Mapbox, Flo's Tileserver, Google and Mapquest
- Geocoding: OSM Nominatim and Mapbox
- Map Frontends: PMSF, RocketMAD and RDM
