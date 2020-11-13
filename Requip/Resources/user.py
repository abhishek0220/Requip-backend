from flask_restful import Resource, reqparse
from flask import Response
from Requip import db
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        parser.add_argument('phone_number', help = 'This field can be blank', required = False)
        data = parser.parse_args()
        username = data['username']
        email = data['email']
        password = data['password']
        phone_number = data['phone_number']
        if(db.users.find_one({'email': email}) or db.users.find_one({'username' : username})):
            return {'message': 'User already exists'}
        user = {
            'username' : username,
            'email' : email,
            'password' : password,
            'phone_number' : phone_number
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

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help = 'This field can be blank', required = False)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        _id = data['id']
        password = data['password']
        if('@' in _id):
            user = db.users.find_one({'email': _id })
        else:
            user = db.users.find_one({'username': _id })
        if(user):
            if(user['password'] == password):
                access_token = create_access_token(identity = user['username'])
                refresh_token = create_refresh_token(identity = user['username'])
                return {
                'message': 'Logging in User {}'.format(user['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
            else:
                return {'message': 'Invalid Credentials'}
        else:
            return {'message': 'User does not exists'}

class UserProfile(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field can be blank', required = True)
        data = parser.parse_args()
        _username = data['username']
        if (db.users.find_one({'username': _username})):
            return db.users.find_one({'username': _username})
        else:
            return {'message': 'User does not exists'}