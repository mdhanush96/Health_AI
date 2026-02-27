-- MySQL initialization script for MyHealth AI

CREATE DATABASE IF NOT EXISTS health_ai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE health_ai_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON health_ai_db.* TO 'health_user'@'%';
FLUSH PRIVILEGES;
