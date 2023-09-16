from flask import Flask;
from flask import request,jsonify

from configuration import Configuration;
from flask_jwt_extended import JWTManager
from auth import authentication_required, owner_required

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import os

app = Flask (__name__);
app.config.from_object (Configuration);
jwt = JWTManager ( app )


@app.route ("/product_statistics", methods=["GET"])
def product_statistics ( ):
    spark =  SparkSession.builder.appName("Spark server").master("local[*]").config ("spark.driver.extraClassPath", "mysql-connector-j-8.0.33.jar").getOrCreate()
    # Connect to MySQL and fetch data using Spark
    database_url = "jdbc:mysql://database:3306/store"
    database_properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.cj.jdbc.Driver"
    }
    
    # Read data from the products and order_products tables
    products_df = spark.read.jdbc(database_url, "products", properties=database_properties)
    order_products_df = spark.read.jdbc(database_url, "order_products", properties=database_properties)
    orders_df = spark.read.jdbc(database_url, "orders", properties=database_properties)

    result_df = order_products_df \
        .join(orders_df, order_products_df.order_id == orders_df.id) \
        .join(products_df, order_products_df.product_id == products_df.id) \
        .groupBy("name") \
        .agg(
            F.coalesce(F.sum(F.when(F.col("status") == "COMPLETE", F.col("quantity"))), F.lit(0)).alias("sold"),
            F.coalesce(F.sum(F.when(F.col("status") != "COMPLETE", F.col("quantity"))), F.lit(0)).alias("waiting")
        ) \
        .filter((F.col("sold") > 0) | (F.col("waiting") > 0))
    result_list = [row.asDict() for row in result_df.collect()]

    return jsonify(statistics=result_list), 200



@app.route ("/category_statistics", methods=["GET"])
def category_statistics ( ):
    return "", 200

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5004 )