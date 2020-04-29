from configparser import ConfigParser

class create_config:
    def __init__(self, config_path):
        config_file = ConfigParser()
        config_file.read("default.ini")
        config_file.read(config_path)

        self.language = config_file.get("Config", "language").lower()
        self.scraper_wait = config_file.getint("Config", "portal_scraper_interval")


        self.use_static_map = config_file.getboolean("Maps", "static_map")
        self.static_provider = config_file.get("Maps", "static_map_provider").lower()
        self.static_key = config_file.get("Maps", "key")

        self.use_map = config_file.getboolean("Maps", "frontend_map")
        self.map_url = config_file.get("Maps", "map_url")
        self.map_provider = config_file.get("Maps", "frontend").lower()
        self.map_name = config_file.get("Maps", "map_name")

        self.use_geocoding = config_file.getboolean("Maps", "geocoding")
        self.geocoding_provider = config_file.get("Maps", "geocoding_provider").lower()
        self.geocoding_key = config_file.get("Maps", "geocoding_key")

        self.zoom = config_file.get("Maps", "zoom", fallback="17")
        self.width = config_file.get("Maps", "width", fallback="800")
        self.height = config_file.get("Maps", "height", fallback="500")


        self.scan_type = config_file.get("DB", "scanner").lower()
        self.db_name_scan = config_file.get("DB", "scanner_db_name")
        self.db_name_portal = config_file.get("DB", "portal_db_name")

        self.db_host = config_file.get("DB", "host")
        self.db_port = config_file.getint("DB", "port")
        self.db_user = config_file.get("DB", "user")
        self.db_password = config_file.get("DB", "password")