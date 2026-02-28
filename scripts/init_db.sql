-- MySQL initialization script for MyHealth AI

CREATE DATABASE IF NOT EXISTS health_ai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE health_ai_db;

-- Create/reset application user for both local and containerized access
CREATE USER IF NOT EXISTS 'health_user'@'localhost' IDENTIFIED BY 'health_password';
CREATE USER IF NOT EXISTS 'health_user'@'%' IDENTIFIED BY 'health_password';
ALTER USER 'health_user'@'localhost' IDENTIFIED BY 'health_password';
ALTER USER 'health_user'@'%' IDENTIFIED BY 'health_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON health_ai_db.* TO 'health_user'@'localhost';
GRANT ALL PRIVILEGES ON health_ai_db.* TO 'health_user'@'%';
FLUSH PRIVILEGES;
