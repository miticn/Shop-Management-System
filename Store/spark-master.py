from flask import Flask;
from configuration import Configuration;
from pyspark.sql import SparkSession
from os import environ
app = Flask (__name__);
app.config.from_object (Configuration);

spark = SparkSession.builder \
    .appName("FlaskSparkApp") \
    .master(Configuration.SPARK_MASTER_URI) \
    .getOrCreate()

@app.route ("/product_statistics", methods=["GET"])
def product_statistics ( ):
    return "Product statistics", 200;

@app.route ("/category_statistics", methods=["GET"])
def category_statistics ( ):
    return "", 200;


if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5004 )