CREATE DATABASE flaskapp;
use flask_app;
CREATE TABLE accounts (
    ID int NOT NULL,
    FirstName varchar(255),
    LastName varchar(255),
    Password varchar(255),
    Address varchar(255),
    email varchar(255),
    City varchar(255),
    PRIMARY KEY (ID)
    
 );