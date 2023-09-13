from functools import wraps
from flask import request
from flask_jwt_extended import decode_token
def authentication_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Authorization" not in request.headers:
            return {"msg": "Missing Authorization Header"}, 401

        authorization_header = request.headers["Authorization"]
        token_parts = authorization_header.split(" ")

        if len(token_parts) != 2 or token_parts[0] != "Bearer":
            return {"msg": "Invalid Authorization Header"}, 401

        token = token_parts[1]
        try:
            claims = decode_token(token)
        except Exception as e:
            return {"msg": "Invalid Token"}, 401

        kwargs['claims'] = claims
        return f(*args, **kwargs)

    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = kwargs['claims']
        print(claims["roles"])
        print("owner" not in claims["roles"])
        if "owner" not in claims["roles"]:
            return {"msg": "Missing Authorization Header"}, 401
        kwargs['claims'] = claims
        return f(*args, **kwargs)

    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = kwargs['claims']
        if "customer" not in claims["roles"]:
            return {"msg": "Missing Authorization Header"}, 401
        kwargs['claims'] = claims
        return f(*args, **kwargs)

    return decorated_function