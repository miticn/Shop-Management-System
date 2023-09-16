from flask import Flask;
from flask import request,jsonify
from models import Product, Category, ProductCategories;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager, decode_token
from auth import authentication_required, owner_required

import requests
from os import environ

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder \
    .appName("FlaskSparkApp") \
    .master("spark://localhost:7077") \
    .getOrCreate()

app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )


@app.route ("/update", methods=["POST"])
@authentication_required
@owner_required
def update ( claims):
    print("Update reached")
    #check if file is present
    if not "file" in request.files:
        return {"message": "Field file is missing."}, 400;
    #get file
    file = request.files["file"];
    lines = file.read ( ).decode ( "utf-8" ).split ( "\n" );
    for line_number in range ( len ( lines ) ):
        lines[line_number] = lines[line_number].split ( "," );
        if len (lines[line_number]) != 3:
            return {"message": "Incorrect number of values on line "+str(line_number)+"."}, 400
        try:
            price = float (lines[line_number][2]);
            if price < 0:
                return {"message": "Incorrect price on line "+str(line_number)+"."}, 400
        except ValueError:
            return {"message": "Incorrect price on line "+str(line_number)+"."}, 400
        
        #check if product already exists
        product = Product.query.filter_by(name = lines[line_number][1]).first ( );
        if product != None:
            return {"message": "Product "+lines[line_number][1]+" already exists."}, 400
    
    for line in lines:
        product = Product (name = line[1], price = line[2]);
        categories = [category.strip() for category in line[0].split ( "|" )]
        print(categories)
        database.session.add (product);
        database.session.commit ( );
        for category_name in categories:
            category = Category.query.filter_by(name = category_name).first ( );
            print("Category: ", category)
            if category == None:
                category = Category (name = category_name)
                database.session.add (category);
            print("Category: ", category.name)
            database.session.commit ( );
            product_category = ProductCategories (product_id = product.id, category_id = category.id);
            database.session.add (product_category);
    
    database.session.commit ( );

    
    return "", 200;


@app.route ("/product_statistics", methods=["GET"])
@authentication_required
def product_statistics ( ):
    # Connect to MySQL and fetch data using Spark
    database_url = "jdbc:mysql://database:33066/store"
    database_properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.jdbc.Driver"
    }
    
    # Read data from the products and order_products tables
    products_df = spark.read.jdbc(database_url, "products", properties=database_properties)
    order_products_df = spark.read.jdbc(database_url, "order_products", properties=database_properties)
    orders_df = spark.read.jdbc(database_url, "orders", properties=database_properties)

    # Join and aggregate data to get statistics
    result_df = order_products_df.join(orders_df, "order_id") \
        .join(products_df, "product_id") \
        .groupBy("product_id", "name") \
        .agg(
            F.sum(F.when(F.col("status") == "delivered", F.col("quantity"))).alias("sold"),
            F.sum(F.when(F.col("status") != "delivered", F.col("quantity"))).alias("waiting")
        ) \
        .filter(F.col("sold") > 0)

    # Convert the Spark DataFrame to a Python list of dictionaries
    result_list = [row.asDict() for row in result_df.collect()]

    # Return the result as JSON
    return jsonify(statistics=result_list),200

@app.route ("/category_statistics", methods=["GET"])
@authentication_required
def category_statistics ( ):
    response = requests.get(f'http://{environ["SPARK_URL"]}:5004/category_statistics')
    return response.content, response.status_code

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5001 )