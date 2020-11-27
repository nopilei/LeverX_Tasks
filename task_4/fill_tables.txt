INSERT IGNORE INTO room (`id`, `name`) VALUES (%s, %s);

INSERT IGNORE INTO student (`id`, `name`, `sex`, `room_id`, `birthday`) VALUES (%s, %s, %s, %s, %s);