from flask_restful import Resource, reqparse
from flask import Response
from app import db
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        username = data['username']
        email = data['email']
        password = data['password']
        if(db.users.find_one({'email': email}) or db.users.find_one({'username' : username})):
            return {'message': 'User already exists'}
        user = {
            'username' : username,
            'email' : email,
            'password' : password
        }
        try:
            db.users.insert(user)
        except:
            return {'message' : "Some Error"}
        else:
            access_token = create_access_token(identity = username)
            refresh_token = create_refresh_token(identity = username)
            return {
            'message': 'User {} was created'.format(data['username']),
            'access_token': access_token,
            'refresh_token': refresh_token
            }

