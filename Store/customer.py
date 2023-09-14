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


@app.route ("/order", methods=["POST"])
@authentication_required
@customer_required
def order ( claims):
    request_data = request.get_json ( );
    if not "requests" in request_data:
        return {"message": "Field requests is missing."}, 400;
    requests = request_data["requests"];

    for req_i in range(len(requests)):
        if not "id" in requests[req_i]:
            return {"message": "Product id is missing for request number "+str(req_i)+"."}, 400;
        if not "quantity" in requests[req_i]:
            return {"message": "Product quantity is missing for request number "+str(req_i)+"."}, 400;
        try:
            product_id = int(requests[req_i]["id"]);
        except ValueError:
            return {"message": "Invalid product id for request number "+str(req_i)+"."}, 400;
        if product_id < 0:
            return {"message": "Invalid product id for request number "+str(req_i)+"."}, 400;
        try:
            quantity = int(requests[req_i]["quantity"]);
        except ValueError:
            return {"message": "Invalid product quantity for request number "+str(req_i)+"."}, 400;
        if quantity < 0:
            return {"message": "Invalid product quantity for request number "+str(req_i)+"."}, 400;
        product = Product.query.filter_by(id = product_id).first ( );
        if product == None:
            return {"message": "Invalid product for request number "+str(req_i)+"."}, 400;

    return "", 200;

@app.route ("/status", methods=["GET"])
@authentication_required
@customer_required
def status ( claims):
    return "", 200;

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5002 )