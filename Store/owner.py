from flask import Flask;
from flask import request
from models import Product, Category, ProductCategories;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager, decode_token

app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )


@app.route ("/update", methods=["POST"])
def update ( ):
    data = request
    return "ok", 200;


if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True )