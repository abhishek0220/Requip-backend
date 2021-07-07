from flask_restful import Resource, reqparse, request
from flask import Response, render_template
from Requip import db
from flask_jwt_extended import (create_access_token, decode_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, jwt_optional)
import os, shutil
import base64, uuid, time
from datetime import datetime, timedelta 
from io import BytesIO
from PIL import Image
from hashlib import sha256
# import sendgrid
# from sendgrid.helpers.mail import *
from Requip.azureStorage import FileManagement
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from Requip import limiter
from Requip.Resources.extra import get_user_id_with_jwt

class UserRegistration(Resource):
    decorators = [limiter.limit("5/second")]
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('name', help = 'This field cannot be blank', required = True)
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        parser.add_argument('phone_number', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        username = data['username'].lower()
        email = data['email'].lower()
        password = data['password']
        name = data['name']
        phone_number = data['phone_number']
        if( (username.isalnum() == False) or (len(email)<=15) or (email[-15:] != '@iitjammu.ac.in') or (phone_number.isnumeric() == False) or int(phone_number) < 6000000000 or int(phone_number) > 9999999999):
            return {'message': 'invalid params'}
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
            'about' : "My text by default",
            'isactive' : False,
            'last_reset_request' : int(time.time()),
            'last_reset' : int(time.time())
        }
        try:
            db.users.insert(user)
        except:
            return {'message' : "Some Error"}
        else:
            def_img = os.path.join(os.getenv('FILES'),'user.jpg')
            FileManagement.upload(img_loc,def_img)
            tok_pre = bytes(username+user['password']+str(user['last_reset'])+str(user['last_reset_request']), 'ascii')
            tok_pre_en = sha256(tok_pre).hexdigest()
            identity = {
                'username':username,
                'token' : tok_pre_en
            }
            # disabled email feature because of send-grid limitations
            # You can turn it on 
            """
            tok_final = create_access_token(identity = identity, expires_delta= timedelta(minutes= 5))
            token_url = os.getenv('FRONTEND') + f'/verify/{username}/{tok_final}'
            resp = render_template('verify.html', user_name = username, token = token_url)
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email("requip@iamabhishek.live")
            to_email = To(user['email'])
            subject = "Welcome to Requip"
            content = Content("text/html", resp)
            mail = Mail(from_email, to_email, subject, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            """
            return {
            'message': 'User {} is created'.format(data['username']),
            'username' : f"{data['username']}"
            }

class UserLogin(Resource):
    decorators = [limiter.limit("5/second")]
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        if('@' in data['id']):
            user = db.users.find_one({'email': data['id'].lower() })
        else:
            user = db.users.find_one({'username': data['id'].lower() })
        if(user):
            if(user['password'] == data['password'] and user.get('isactive', False)):
                access_token = create_access_token(identity = user['username'])
                refresh_token = create_refresh_token(identity = user['username'])
                return {
                'message': 'Logging in User {}'.format(user['username']),
                'name': user['name'],
                'image': user['image'],
                'username':user['username'],
                'access_token': access_token,
                'refresh_token': refresh_token
                }
                print(user['name'] + user['username'])
                print("yes")
            else:
                return {'message': 'Invalid Credentials or account disabled'}
        else:
            return {'message': 'User does not exists'}

class UserReset(Resource):
    decorators = [
        limiter.limit("1/second", methods=["GET"]),
        limiter.limit("1/second", methods=["POST"])
    ]
    def get(self, username):
        username = username.lower()
        user = db.users.find_one({'username':username}, {'_id' : 1, 'email':1, 'password':1, 'username':1, 'last_reset_request' : 1, 'last_reset' : 1 })
        if(user == None):
            return {'message': 'User does not exists'}
        last_req  = user.get('last_reset_request', 0)
        last_rest = user.get('last_reset', 0)
        curr_time = int(time.time())
        if((curr_time - last_req) < 300 ):
            return {'message': 'Please wait 5 min before making request again'}
        db.users.update_one({'username':username}, { "$set": {'last_reset_request':curr_time} })
        tok_pre = bytes(username+user['password']+str(last_rest)+str(curr_time), 'ascii')
        tok_pre_en = sha256(tok_pre).hexdigest()
        identity = {
            'username':username,
            'token' : tok_pre_en
        }
        # disabled email feature because of send-grid limitations
        """
        tok_final = create_access_token(identity = identity, expires_delta= timedelta(minutes= 5))
        token_url = os.getenv('FRONTEND') + f'/reset/{username}/{tok_final}'
        resp = render_template('forget.html', user_name = username, token = token_url)
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email("requip@iamabhishek.live")
        to_email = To(user['email'])
        subject = "Reset Requip Password"
        content = Content("text/html", resp)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response)
        """
        return {'message': 'Email Sent'}

    def post(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('token', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        password = data.get('password', None)
        token = data['token']
        token_rev = decode_token(token, allow_expired=False)
        user = db.users.find_one({'username':username}, {'_id' : 1, 'email':1, 'password':1, 'username':1, 'last_reset_request' : 1, 'last_reset' : 1 })
        if(user == None):
            return {'message': 'User does not exists'}
        identity = token_rev['identity']
        token = identity['token']
        last_rest = user.get('last_reset',0)
        curr_time = user.get('last_reset_request',0)
        new_token = bytes(username+user['password']+str(last_rest)+str(curr_time), 'ascii')
        new_token_en = sha256(new_token).hexdigest()
        if(token != new_token_en):
            return {'message': 'Invalid Token'}
        curr_time = int(time.time())
        toUpdate = {'last_reset':curr_time, 'isactive' : True}
        toUpdate['password'] = password
        db.users.update_one({'username':username}, { "$set": toUpdate })
        return {'message': 'Success', 'status' : 200}

class UserVerify(Resource):
    decorators = [
        limiter.limit("1/second", methods=["POST"])
    ]
    def post(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('token', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        token = data['token']
        token_rev = decode_token(token, allow_expired=False)
        user = db.users.find_one({'username':username}, {'_id' : 1, 'email':1, 'password':1, 'username':1, 'last_reset_request' : 1, 'last_reset' : 1 })
        if(user == None):
            return {'message': 'User does not exists'}
        identity = token_rev['identity']
        token = identity['token']
        last_rest = user.get('last_reset',0)
        curr_time = user.get('last_reset_request',0)
        print(last_rest)
        print(curr_time)
        new_token = bytes(username+user['password']+str(last_rest)+str(curr_time), 'ascii')
        new_token_en = sha256(new_token).hexdigest()
        if(token != new_token_en):
            return {'message': 'Invalid Token'}
        curr_time = int(time.time())
        toUpdate = {'last_reset':curr_time, 'isactive' : True}
        db.users.update_one({'username':username}, { "$set": toUpdate })
        return {'message': 'Success', 'status' : 200}

class UserProfile(Resource):
    decorators = [limiter.limit("5/second")]
    def get(self, username):
        user = db.users.find_one({'username': username.lower()})
        if (user != None):
            del user['_id']
            del user['password']
            del user['phone']
            return user
        else:
            return {'message': 'User does not exists'}

class ChangeProfilePic(Resource):
    decorators = [
        limiter.limit("5/minute", key_func=get_user_id_with_jwt ,methods=["POST"])
    ]
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
    decorators = [
        limiter.limit("1/second", key_func=get_user_id_with_jwt, methods=["POST"])
    ]
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
    decorators = [limiter.limit("5/second", key_func=get_user_id_with_jwt)]
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
    decorators = [
        limiter.limit("5/second", methods=["POST"])
    ]
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}
