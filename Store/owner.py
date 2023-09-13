from flask import Flask;
from flask import request
from models import Product, Category, ProductCategories;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager, decode_token
from auth import authentication_required

app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )


@app.route ("/update", methods=["POST"])
@authentication_required
def update ( claims):
    #check if file is present
    if not "file" in request.files:
        return {"message": "Field file missing."}, 400;
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
        product = Category.query.filter_by (name = lines[line_number][1]).first ( );
        if product != None:
            return {"message": "Product "+lines[line_number][1]+" already exists."}, 400

    
    return "ok", 200;


@app.route ("/product_statistics", methods=["GET"])
def product_statistics ( ):
    pass

@app.route ("/category_statistics", methods=["GET"])
def category_statistics ( ):
    pass

if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True, port = 5001 )