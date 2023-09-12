from flask import Flask;
from flask import request
from models import User;
from models import database;

from configuration import Configuration;
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager, decode_token

app = Flask (__name__);
app.config.from_object (Configuration);
database.init_app ( app )
jwt = JWTManager ( app )
def register (role):
    fields = ["forename", "surname", "email", "password"];
    #return 404 if field is missing with message field in json
    for field in fields:
        if not field in request.json or request.json[field] == "":
            return {"message": "Field " + field + " is missing"}, 400;
    
    #return 404 if email is not valid
    if not "@" in request.json["email"] or not "." in request.json["email"]:
        return {"message": "Invalid email."}, 400;

    #return 404 if password is not valid
    if len (request.json["password"]) < 8:
        return {"message": "Invalid password."}, 400

    #return 404 if email is already in use
    if User.query.filter_by (email = request.json["email"]).first ( ) != None:
        return {"message": "Email already exists."}, 400;

    #add customer to database
    user = User (forename = request.json["forename"], surname = request.json["surname"], email = request.json["email"], password = request.json["password"], role = role);
    database.session.add (user);
    database.session.commit ( );
    
    return "",200;

def tokenValid(token : str) -> bool:
    pass

@app.route ("/register_customer", methods=["POST"])
def register_customer ( ):
    return register ("customer");

@app.route ("/register_courier", methods=["POST"])
def register_courier ( ):
    return register ("courier");

@app.route ("/login", methods=["POST"])
def login ( ):
    fields = ["email", "password"];
    #return 404 if field is missing with message field in json
    for field in fields:
        if not field in request.json or request.json[field] == "":
            return {"message": "Field " + field + " is missing"}, 400;

    #check if email is valid
    if not "@" in request.json["email"] or not "." in request.json["email"]:
        return {"message": "Invalid email."}, 400;

    #check credentials from database
    user = User.query.filter_by (email = request.json["email"], password = request.json["password"]).first ( );
    if user == None:
        return {"message": "Invalid credentials."}, 400;

    #create token
    claims = {
            "forename": user.forename,
            "surname": user.surname,
            "roles": [user.role]
    }
    access_token  = create_access_token ( identity = user.email, additional_claims = claims )

    return {"accessToken":access_token},200;
    

@app.route ("/delete", methods=["POST"])
def delete ( ):
    #return 404 if field is missing with message field in json
    if not "Authorization" in request.json or request.json["Authorization"] == "" or request.json["Authorization"].split (" ")[0] != "Bearer":
        return {"msg": "Missing Authorization Header"}, 401;

    token = request.json["Authorization"].split (" ")[1];
    app.logger.info (token);
    #return 404 if token is invalid
    try:
        claims = decode_token (token);
        app.logger.info (claims);
    except Exception as e:
        app.logger.info (str(e));
        return {"msg": "Missing Authorization Header"}, 401;

    #delete from model
    user = User.query.filter_by (email = claims['sub']).first ( );
    if user == None:
        return {"message": "Unknown user."}, 400;
    database.session.delete (user);
    database.session.commit ( );
    return "",200;

    


    
    
if ( __name__ == "__main__" ):
    app.run ( host="0.0.0.0", debug = True )