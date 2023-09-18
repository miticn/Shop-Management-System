from flask import Flask;
from flask import request
from models import Product, Category, Order,OrderProducts;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import JWTManager
from auth import authentication_required, customer_required
from datetime import datetime
from web3 import Web3, HTTPProvider
import json
app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )
web3 = Web3(HTTPProvider(f"{Configuration.WEB3_PROVIDER_URI}"))

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

    order_price : float = 0;
    order_items = [];
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
        order_price += product.price * quantity;
        order_items.append((product_id, quantity));
    
    if "address" not in request_data:
        return {"message": "Field address is missing."}, 400;
    if request_data["address"] == "":
        return {"message": "Field address is missing."}, 400;
    
    if not web3.is_address(request_data["address"]):
        return {"message": "Invalid address."}, 400;
    
    #create contract
    owner_account = web3.eth.account.from_key(Configuration.OWNER_PRIVATE_KEY);
    contract = web3.eth.contract(abi = Configuration.CONTRACT_ABI, bytecode = Configuration.CONTRACT_BYTECODE);
    tx_hash = contract.constructor(request_data["address"],int(order_price)).transact(
        {
            "from": owner_account.address
        }
    );
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash);
    contract_address = tx_receipt.contractAddress;
    

    #create order
    order = Order ( customer_email = claims["sub"], price = order_price, status = "CREATED", timestamp = datetime.now ( ), contract_address = contract_address );
    database.session.add ( order );
    database.session.commit ( );
    for item in order_items:
        database.session.add(OrderProducts(order_id = order.id, product_id = item[0], quantity = item[1]));
    database.session.commit ( );
    return {"id": order.id}, 200;





@app.route ("/status", methods=["GET"])
@authentication_required
@customer_required
def status ( claims):
    customer_email = claims["sub"];
    orders = Order.query.filter_by(customer_email = customer_email).all ( );
    return {"orders": [order.to_json() for order in orders]}, 200;

@app.route ("/delivered", methods=["POST"])
@authentication_required
@customer_required
def delivered ( claims):
    #get order id
    request_data = request.get_json ( );
    if not "id" in request_data:
        return {"message": "Missing order id."}, 400;
    try:
        order_id = int(request_data["id"]);
    except ValueError:
        return {"message": "Invalid order id."}, 400;
    if order_id < 0:
        return {"message": "Invalid order id."}, 400;

    #get order
    order = Order.query.filter_by(id = order_id).first ( );
    if order == None:
        return {"message": "Invalid order id."}, 400;
    if order.customer_email != claims["sub"]:
        return {"message": "Invalid order id."}, 400;
    if order.status != "PENDING":
        return {"message": "Invalid order id."}, 400;

    #get keys
    if not "keys" in request_data or request_data["keys"] == "":
        return {"message": "Missing keys."}, 400;

    if not "passphrase" in request_data or request_data["passphrase"] == "":
        return {"message": "Missing passphrase."}, 400;
    #decrypt keys
    try:
        keys = json.loads(request_data["keys"].replace("'", "\""));
        print(keys)
        costomerAccountPrK = web3.eth.account.decrypt(keys, request_data["passphrase"]);
        costomerAccount = web3.eth.account.from_key(costomerAccountPrK)
        print(costomerAccount)
    except ValueError:
        print(ValueError)
        return {"message": "Invalid credentials."}, 400;

    #get contract
    contract = web3.eth.contract(address = order.contract_address, abi = Configuration.CONTRACT_ABI);

    #check if address is the same
    if contract.functions.buyer().call() != costomerAccount.address:
        return {"message": "Invalid customer account."}, 400;

    #check if paid
    if contract.functions.state().call() < 1:
        return {"message": "Transfer not complete."}, 400;

    #check if picked up
    if contract.functions.state().call() < 2:
        return {"message": "Delivery not complete."}, 400;


    transaction = contract.functions.delivered().build_transaction({
        "from": costomerAccount.address,
        "nonce": web3.eth.get_transaction_count(costomerAccount.address),
        "gasPrice": web3.eth.gas_price
    })

    signed_transaction = web3.eth.account.sign_transaction(transaction, costomerAccountPrK)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

    order.status = "COMPLETE";
    database.session.commit ( );
    return "", 200;

@app.route ("/pay", methods=["POST"])
@authentication_required
@customer_required
def pay ( claims):
    #get order id
    request_data = request.get_json ( );
    if not "id" in request_data:
        return {"message": "Missing order id."}, 400;
    try:
        order_id = int(request_data["id"]);
    except ValueError:
        return {"message": "Invalid order id."}, 400;
    if order_id < 0:
        return {"message": "Invalid order id."}, 400;
    order = Order.query.filter_by(id = order_id).first ( );
    if order == None:
        return {"message": "Invalid order id."}, 400;
    #get keys
    if not "keys" in request_data or request_data["keys"] == "":
        return {"message": "Missing keys."}, 400;
    
    if not "passphrase" in request_data or request_data["passphrase"] == "":
        return {"message": "Missing passphrase."}, 400;

    #decrypt keys
    
    try:
        keys = json.loads(request_data["keys"].replace("'", "\""));
        print(keys)
        costomerAccountPrK = web3.eth.account.decrypt(keys, request_data["passphrase"]);
        costomerAccount = web3.eth.account.from_key(costomerAccountPrK)
        print(costomerAccount)
    except ValueError:
        return {"message": "Invalid credentials."}, 400;

    #get contract
    contract = web3.eth.contract(address = order.contract_address, abi = Configuration.CONTRACT_ABI);

    #check if funds are enough
    if web3.eth.get_balance(costomerAccount.address) < contract.functions.cost().call():
        print(web3.eth.get_balance(costomerAccount.address))
        print(contract.functions.cost().call())
        return {"message": "Insufficient funds."}, 400;

    #check if already paid
    if contract.functions.state().call() != 0:
        return {"message": "Transfer already complete."}, 400;
    
    #pay
    try:
        transaction = contract.functions.pay().build_transaction({
            "from": costomerAccount.address,
            "nonce": web3.eth.get_transaction_count(costomerAccount.address),
            "gasPrice": web3.eth.gas_price,
            "value": contract.functions.cost().call()
        })
        signed_transaction = web3.eth.account.sign_transaction(transaction, costomerAccountPrK)
        transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    except ValueError:
        return {"message": "Insufficient funds."}, 400;

    return "", 200;

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5002 )