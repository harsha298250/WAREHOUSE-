-- Run this in MySQL Workbench or the mysql command line before starting the app.
-- (You can change the password below — just update it in your .env file too.)

CREATE DATABASE IF NOT EXISTS warehouse_db;
CREATE USER IF NOT EXISTS 'warehouse_app'@'localhost' IDENTIFIED BY 'YOUR_SECURE_DB_PASSWORD';
GRANT ALL PRIVILEGES ON warehouse_db.* TO 'warehouse_app'@'localhost';
FLUSH PRIVILEGES;
