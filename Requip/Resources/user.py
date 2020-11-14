from flask_restful import Resource, reqparse
from flask import Response
from Requip import db
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
import os, shutil

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
            'phone' : phone_number
        }
        try:
            db.users.insert(user)
        except:
            return {'message' : "Some Error"}
        else:
            folder = os.path.join(os.getenv('STATIC'),'users', username)
            post_folder = os.path.join(folder,'posts')
            os.mkdir(folder)
            os.mkdir(post_folder)
            def_img = os.path.join(os.getenv('STATIC'),'user.png')
            tar_img = os.path.join(folder,'user.png')
            shutil.copy(def_img, tar_img)
            return {
            'message': 'User {} was created'.format(data['username']),
            'username' : f"{data['username']}"
            }

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help = 'This field can be blank', required = True)
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
                'username':user['username'],
                'access_token': access_token,
                'refresh_token': refresh_token
                }
            else:
                return {'message': 'Invalid Credentials'}
        else:
            return {'message': 'User does not exists'}

class UserProfile(Resource):
    def get(self, username):
        obj = db.users.find_one({'username': username})
        if (obj != None):
            _username = obj["username"]
            _email = obj["email"]
            try :
                _phone = obj["phone"]
            except :
                _user = {
                    'username' : _username,
                    'email' : _email,
                }
            else:
                _user = {
                    'username' : _username,
                    'email' : _email,
                    'phone_number' : phone_number
                }
            return _user
        else:
            return {'message': 'User does not exists'}

class UserProfileUpdate(Resource):
    @jwt_required
    def post(self):
        _user = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('about', help = 'This field can be blank', required = False)
        parser.add_argument('phone', help = 'This field can be blank', required = False)
        data = parser.parse_args()
        _about = data['about']
        _phone = data['phone']

        query = { "username": _user }
        values = {}

        if (db.users.find_one(query)):
            if _about != None:
                values['about'] = _about
            if _phone != None:
                values['phone'] = _phone

            # print(values)
            query_update = { "$set": values }

            try:
                db.users.update_one(query, query_update)
                return {"message" : "Information updated successfully"}
            except Exception as e:
                print("could not able to update the info")
                print("Exception", e)
                return {"message": "Sorry due to some reason the information is not updated..!!"}
        else:
            return {"message": "User does not exists"}
          
class User(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        user = db.users.find_one({'username': username})
        if (user != None):
            del user['_id']
            del user['password']
            return user
        else:
            return {'message': 'User does not exists'}

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}
