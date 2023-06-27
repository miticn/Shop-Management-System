create database users;
use users;

create table users (
    id int primary key auto_increment,
    forename varchar(256) not null,
    surname varchar(256) not null,
    email varchar(256) not null,
    password varchar(256) not null,
    role varchar(256) not null
);