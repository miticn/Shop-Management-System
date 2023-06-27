from datetime import timedelta

class Configuration:
    SQLALCHEMY_DATABASE_URI   = "mysql://root:root@database:3306/users"
    JWT_SECRET_KEY            = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta ( minutes = 15 );
    JWT_REFRESH_TOKEN_EXPIRES = timedelta ( days = 30 );