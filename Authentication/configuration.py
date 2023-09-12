from datetime import timedelta
from os import environ

class Configuration:
    #127.0.0.1
    #CHECK ENVIRONMENT VARIABLES
    if "DOCKER_INSTANCE" in environ:
        DATABASE_URL = "database"
    else:
        DATABASE_URL = "127.0.0.1"
    SQLALCHEMY_DATABASE_URI   = f"mysql://root:root@{DATABASE_URL}:3306/users"
    JWT_SECRET_KEY            = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta ( minutes = 60 );
    JWT_REFRESH_TOKEN_EXPIRES = timedelta ( days = 30 );