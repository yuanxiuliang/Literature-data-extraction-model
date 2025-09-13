-- 初始化数据库脚本
-- 创建数据库和用户（如果不存在）

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS crystal_growth 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE crystal_growth;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON crystal_growth.* TO 'app_user'@'%';
FLUSH PRIVILEGES;

-- 设置外键检查
SET FOREIGN_KEY_CHECKS = 1;
