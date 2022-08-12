CREATE TABLE IF NOT EXISTS `sw_fort` (
  `id` varchar(64) NOT NULL,
  `game_id` tinyint NOT NULL,
  # 0 = unknown, 10 = pogo, 20 = ingress, 30 = lightship
  `type_id` tinyint NOT NULL,
  # 0 = unknown, 10 = gym, 15 = pokestop, 20 = portal, 30 = lighship_poi
  `lat` double NOT NULL,
  `lon` double NOT NULL,
  `name` varchar(128) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `cover_image` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`, `game_id`)
);