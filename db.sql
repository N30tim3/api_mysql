drop database if exists apimysql;
create database apimysql;
use apimysql;
CREATE TABLE user (
  id int NOT NULL AUTO_INCREMENT,
  username varchar(45) DEFAULT NULL,
  password varchar(255) DEFAULT NULL,
  email varchar(255) DEFAULT NULL,
  PRIMARY KEY (id)
);
