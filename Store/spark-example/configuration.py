from datetime import timedelta
from os import environ

class Configuration:
    #127.0.0.1
    #CHECK ENVIRONMENT VARIABLES
    if "DOCKER_INSTANCE" in environ:
        DATABASE_URL = "database"
    else:
        DATABASE_URL = "127.0.0.1"
    if "SPARK_INSTANCE" in environ:
        SPARK_URL = "spark-master"
    else:
        SPARK_URL = "127.0.0.1"

    SQLALCHEMY_DATABASE_URI   = f"mysql://root:root@{DATABASE_URL}:33066/store"
    SPARK_MASTER_URI          = f"spark://{SPARK_URL}:7077"
    JWT_SECRET_KEY            = "JWT_SECRET_DEV_KEY"