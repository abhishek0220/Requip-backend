from flask_restful import Resource, reqparse, request
from flask import Response
from Requip import db
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
import os, shutil
import base64, uuid
from io import BytesIO
from PIL import Image
from Requip.azureStorage import FileManagement

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('name', help = 'This field cannot be blank', required = True)
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        parser.add_argument('phone_number', help = 'This field can be blank', required = True)
        data = parser.parse_args()
        username = data['username']
        email = data['email']
        password = data['password']
        name = data['name']
        phone_number = data['phone_number']
        if(db.users.find_one({'email': email}) or db.users.find_one({'username' : username})):
            return {'message': 'User already exists'}
        img_loc = f'{username}/{str(uuid.uuid4())}.jpg'
        user = {
            'username' : username,
            'name' : name,
            'email' : email,
            'password' : password,
            'phone' : phone_number,
            'image' : img_loc,
            'about' : "My text by default"
        }
        try:
            db.users.insert(user)
        except:
            return {'message' : "Some Error"}
        else:
            def_img = os.path.join(os.getenv('FILES'),'user.jpg')
            FileManagement.upload(img_loc,def_img)
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
        user = db.users.find_one({'username': username})
        if (user != None):
            del user['_id']
            del user['password']
            return user
        else:
            return {'message': 'User does not exists'}

class ChangeProfilePic(Resource):
    @jwt_required
    def post(self):
        username = get_jwt_identity()
        try:
            _user = db.users.find_one({'username': username})
            if(_user == None):
                return Response("{'message': 'User not exist'}", status=404, mimetype='application/json')
            img_rev = request.data.decode('ascii').split(',')[1]
            image_data = bytes(img_rev, encoding="ascii")
            im = Image.open(BytesIO(base64.b64decode(image_data)))
            if(im.size != (400,400)):
                return Response("{'message': 'Invalid Size'}", status=403, mimetype='application/json')
            tar_loc = f'{username}_{str(uuid.uuid4())}.jpg'
            img_loc = f'{username}/{str(uuid.uuid4())}.jpg'
            file_loc = os.path.join(os.getenv('FILES'),tar_loc)
            im = im.convert("RGB")
            im.save(file_loc)
            FileManagement.upload(img_loc, file_loc)
            FileManagement.delete(_user['image'])
            db.users.update_one({'username':username}, { "$set": {'image':img_loc} })
            os.remove(file_loc)
            return {
                'message': 'Saved Successfully',
                'image':img_loc
                }
        except:
            return Response("{'message': 'Invalid image'}", status=403, mimetype='application/json')

class UserProfileUpdate(Resource):
    @jwt_required
    def post(self):
        _user = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('name', help = 'This field can be blank', required = True)
        parser.add_argument('about', help = 'This field can be blank', required = True)
        parser.add_argument('phone', help = 'This field can be blank', required = True)
        data = parser.parse_args()
        _about = data['about']
        _phone = data['phone']
        _name = data['name']
        query = { "username": _user }
        values = {}
        if (db.users.find_one(query)):
            values['about'] = _about
            values['phone'] = _phone
            values['name'] = _name
            query_update = { "$set": values }
            try:
                db.users.update_one(query, query_update)
                return {"message" : "Information updated successfully"}
            except Exception as e:
                print("could not able to update the info")
                print("Exception", e)
                return Response("{'message': 'Sorry due to some reason the information is not updated..!!'}", status=500, mimetype='application/json')
        else:
            return Response("{'message': 'User not exist'}", status=404, mimetype='application/json')
          
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
