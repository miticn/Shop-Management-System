from flask import Flask;
from flask import request
from models import Product, Category, ProductCategories;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager, decode_token
from auth import authentication_required, customer_required

app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )


@app.route ("/search", methods=["GET"])
@authentication_required
@customer_required
def search ( claims):
    #get parameters
    name = request.args.get ( "name" );
    category = request.args.get ( "category" );

    products = Product.query;
    categories = Category.query;
    if name != None:
        products = products.filter(Product.name.contains(name));
        categories = categories.filter(Category.products.any(Product.name.like(f"%{name}%")))
    if category != None:
        products = products.filter(Product.categories.any(Category.name.like(f"%{category}%")))
        categories = categories.filter(Category.name.contains(category))
    
    products = products.all();
    categories = categories.all();
    return {
        'categories':[category.name for category in categories],
        'products':[product.to_json() for product in products]
        }, 200;

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5002 )