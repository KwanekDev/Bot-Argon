CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `users` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `username` TEXT NOT NULL UNIQUE,
  `password_hash` TEXT NOT NULL,
  `role` TEXT NOT NULL DEFAULT 'user',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `api_keys` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT NOT NULL,
  `key_hash` TEXT NOT NULL UNIQUE,
  `owner_id` INTEGER NOT NULL,
  `scopes` TEXT NOT NULL DEFAULT 'read',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`owner_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
);
