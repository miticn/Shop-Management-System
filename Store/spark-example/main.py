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
# Connect to MySQL and fetch data using Spark
database_url = f"jdbc:mysql://{Configuration.DATABASE_URL}:3306/store"
database_properties = {
    "user": "root",
    "password": "root",
    "driver": "com.mysql.cj.jdbc.Driver"
}

@app.route ("/product_statistics", methods=["GET"])
def product_statistics ( ):
    spark =  SparkSession.builder.appName("product_statistics")\
            .master("spark://spark-master:7077")\
            .config("spark.driver.extraClassPath", "mysql-connector-j-8.0.33.jar")\
            .config("spark.driver.port", "4040") \
            .config("spark.driver.host", "spark-app") \
            .config("spark.driver.bindAddress", "0.0.0.0") \
            .getOrCreate()
    
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
    spark.stop()
    return jsonify(statistics=result_list), 200



@app.route ("/category_statistics", methods=["GET"])

def category_statistics():
    spark =  SparkSession.builder.appName("category_statistics")\
            .master("spark://spark-master:7077")\
            .config("spark.driver.extraClassPath", "mysql-connector-j-8.0.33.jar")\
            .config("spark.driver.port", "4040") \
            .config("spark.driver.host", "spark-app") \
            .config("spark.driver.bindAddress", "0.0.0.0") \
            .getOrCreate()

    # Assuming you've defined your database_url and database_properties elsewhere in your code
    orders = spark.read.jdbc(database_url, "orders", properties=database_properties)
    order_products_df = spark.read.jdbc(database_url, "order_products", properties=database_properties)
    categories_df = spark.read.jdbc(database_url, "categories", properties=database_properties)
    product_categories_df = spark.read.jdbc(database_url, "product_categories", properties=database_properties)

    # Join and count products for each category
    joined_df = categories_df \
        .join(product_categories_df, categories_df.id == product_categories_df.category_id, 'left_outer') \
        .join(order_products_df, product_categories_df.product_id == order_products_df.product_id, 'left_outer') \
        .join(orders, order_products_df.order_id == orders.id, 'left_outer')\
        .groupBy(categories_df.name) \
        .agg(F.sum(F.when(F.col("status") == "COMPLETE", F.col("quantity"))).alias("count_products"))

    # Sort by product count and then category name
    result_df = joined_df.sort(F.desc("count_products"), F.asc("name"))

    result_list = [row['name'] for row in result_df.collect()]

    spark.stop()
    # Assuming you have a jsonify function defined elsewhere in your code
    return jsonify(statistics=result_list), 200

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5004 )