-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: localhost    Database: COMM
-- ------------------------------------------------------
-- Server version	8.0.40-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `BoardList`
--

DROP TABLE IF EXISTS `BoardList`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BoardList` (
  `idBoardList` int unsigned NOT NULL AUTO_INCREMENT,
  `headline` varchar(45) NOT NULL DEFAULT 'Default Headline',
  `proposer_id` int DEFAULT NULL,
  `proposer_name` varchar(45) DEFAULT NULL,
  `propose_time` datetime(1) DEFAULT NULL,
  `start_time` datetime(1) DEFAULT NULL,
  `end_time` datetime(1) DEFAULT NULL,
  `deadline` datetime(1) DEFAULT NULL,
  `content` longtext,
  `college` varchar(45) NOT NULL DEFAULT '北京大学',
  `type` varchar(45) DEFAULT NULL,
  `join_num` int(10) unsigned zerofill DEFAULT '0000000000',
  PRIMARY KEY (`idBoardList`),
  UNIQUE KEY `idBoradList_UNIQUE` (`idBoardList`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ChatMessages`
--

DROP TABLE IF EXISTS `ChatMessages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ChatMessages` (
  `idChatMessages` int unsigned NOT NULL AUTO_INCREMENT,
  `idBoardList` int NOT NULL,
  `sender_id` int NOT NULL,
  `sender_name` varchar(45) NOT NULL,
  `content` longtext NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idChatMessages`),
  UNIQUE KEY `idchat_messages_UNIQUE` (`idChatMessages`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `UserAnnounceDiagram`
--

DROP TABLE IF EXISTS `UserAnnounceDiagram`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserAnnounceDiagram` (
  `idUserAnnounceDiagram` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned NOT NULL,
  `announce_id` int unsigned NOT NULL,
  PRIMARY KEY (`idUserAnnounceDiagram`),
  UNIQUE KEY `idUserAnnounceDiagram_UNIQUE` (`idUserAnnounceDiagram`),
  KEY `user_id_constrant_idx` (`user_id`),
  KEY `announce_id_constrant_idx` (`announce_id`),
  CONSTRAINT `announce_id_constrant` FOREIGN KEY (`announce_id`) REFERENCES `BoardList` (`idBoardList`),
  CONSTRAINT `user_id_constrant` FOREIGN KEY (`user_id`) REFERENCES `UserInfo` (`idUserInfo`)
) ENGINE=InnoDB AUTO_INCREMENT=129 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `UserInfo`
--

DROP TABLE IF EXISTS `UserInfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserInfo` (
  `idUserInfo` int unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `passwoord` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `college` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '北京大学',
  `email` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `is_admin` tinyint NOT NULL DEFAULT '0',
  `bio` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `profile_pictrue` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`idUserInfo`),
  UNIQUE KEY `idUserInfo_UNIQUE` (`idUserInfo`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-22  7:15:14
