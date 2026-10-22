CREATE DATABASE IF NOT EXISTS gestion_inmobiliaria_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'inmo_user'@'localhost' IDENTIFIED BY 'Gestion_2026';

GRANT ALL PRIVILEGES ON gestion_inmobiliaria_db.* TO 'inmo_user'@'localhost';

GRANT ALL PRIVILEGES ON `test\_gestion\_inmobiliaria\_db`.* TO 'inmo_user'@'localhost';

FLUSH PRIVILEGES;