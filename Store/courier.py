from flask import Flask;
from flask import request
from models import Product, Category, Order,OrderProducts;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import JWTManager
from auth import authentication_required, courier_required
from datetime import datetime
from web3 import Web3, HTTPProvider

app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )
web3 = Web3(HTTPProvider("http://localhost:8545"))

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

    if "address" not in request_data or request_data["address"] == "":
        return {"message": "Missing address."}, 400;

    #eth address validation
    if not web3.is_address(request_data["address"]):
        return {"message": "Invalid address."}, 400;

    #contract from order
    contract = web3.eth.contract(address=order.contract_address, abi=Configuration.CONTRACT_ABI);
    #check contract status
    if contract.functions.state().call() != 1:
        return {"message": "Transfer not complete."}, 400;
    #update order
    order.status = "PENDING";
    database.session.commit();

    #pick up order
    owner_account = web3.eth.account.from_key(Configuration.OWNER_PRIVATE_KEY);

    contract.functions.pickUpPackage(request_data["address"]).transact({"from":owner_account.address});
    return "", 200;





if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5003 )