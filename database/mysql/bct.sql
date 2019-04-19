/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 80011
Source Host           : localhost:3306
Source Database       : bct

Target Server Type    : MYSQL
Target Server Version : 80011
File Encoding         : 65001

Date: 2019-04-11 16:09:09
*/

-- 重建数据库
drop database if exists `bct5000`;
create database `bct5000`;

use `bct5000`;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `blockchain`
-- ----------------------------
DROP TABLE IF EXISTS `blockchain`;
CREATE TABLE `blockchain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `block_number` int(11) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `nonce` int(11) NOT NULL,
  `previous_hash` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `block_number` (`block_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of blockchain
-- ----------------------------

-- ----------------------------
-- Table structure for `transactions`
-- ----------------------------
DROP TABLE IF EXISTS `transactions`;
CREATE TABLE `transactions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `block_number` int(11) NOT NULL,
  `sender_address` varchar(255) NOT NULL,
  `recipient_address` varchar(255) NOT NULL,
  `value` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `block_number` (`block_number`)
  -- CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`block_number`) REFERENCES `blockchain` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of transactions
-- ----------------------------
