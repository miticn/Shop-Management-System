from flask import Flask;
from flask import request
from models import Product, Category, Order,OrderProducts;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import JWTManager
from auth import authentication_required, courier_required
from datetime import datetime

app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )


@app.route ("/orders_to_deliver", methods=["GET"])
@authentication_required
@courier_required
def orders_to_deliver ( claims):
    orders = Order.query.filter(Order.status == "CREATED").all();
    return {
        'orders':[
            {
                "id":order.id,
                "email":order.customer_email
            } for order in orders
        ],
    }

@app.route ("/pick_up_order", methods=["POST"])
@authentication_required
@courier_required
def pick_up_order ( claims):
    #get id
    request_data = request.get_json ( );
    if not "id" in request_data:
        return {"message": "Missing order id."}, 400;
    order_id = request_data["id"];
    try:
        order_id = int ( order_id );
    except ValueError:
        return {"message": "Invalid order id."}, 400;
    if order_id <= 0:
        return {"message": "Invalid order id."}, 400;
    #get order
    order = Order.query.filter(Order.id == order_id).first();
    if order == None:
        return {"message": "Invalid order id."}, 400;
    if order.status != "CREATED":
        return {"message": "Invalid order id."}, 400;

    #update order
    order.status = "PENDING";
    database.session.commit();
    return "", 200;





if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5003 )