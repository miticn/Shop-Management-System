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
@authentication_required
@owner_required
def product_statistics ( claims ):
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

    # Join and aggregate data to get statistics
    result_df = order_products_df.join(orders_df, order_products_df.order_id == orders_df.id) \
    .join(products_df, order_products_df.product_id == products_df.id) \
    .groupBy("product_id", "name") \
    .agg(
        F.sum(F.when(F.col("status") == "delivered", F.col("quantity"))).alias("sold"),
        F.sum(F.when(F.col("status") != "delivered", F.col("quantity"))).alias("waiting")
    ) \
    .filter(F.col("sold") > 0)

    # Convert the Spark DataFrame to a Python list of dictionaries
    result_list = [row.asDict() for row in result_df.collect()]

    # Return the result as JSON
    return jsonify(statistics=result_list), 200



@app.route ("/category_statistics", methods=["GET"])
@authentication_required
@owner_required
def category_statistics ( ):
    return "", 200

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5001 )